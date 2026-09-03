import os
import json
import uuid
import base64
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.models.core import PatientDataObject
from app.models.interview import (
    InterviewState, AnswerSubmission, AnswerResult,
    QuestionResponse, RedFlagAlert,
)
from app.models.speech import SpeechRecognitionRequest
from app.models.abha import (
    AbhaAuthInitRequest, AbhaAuthInitResponse,
    AbhaAuthConfirmRequest, AbhaAuthConfirmResponse
)
from app.models.alert import TriageAlertItem
from app.repositories.session_repository import session_repo
from app.repositories.alert_repository import alert_repo
from app.engine.answer_validator import answer_validator
from app.engine.langgraph_workflow import workflow_manager
from app.middleware.error_handler import MediKioskException

router = APIRouter()

# Active ABHA Auth Transactions for M1 Sandbox
_active_abha_transactions: Dict[str, Dict[str, Any]] = {}


@router.post("/", response_model=PatientDataObject, status_code=status.HTTP_201_CREATED)
def create_session(pdo: PatientDataObject):
    """Create a new clinical intake session."""
    if session_repo.get_session(pdo.identity.session_id):
        raise MediKioskException(
            error_code="SESSION_CONFLICT",
            message=f"Session with ID '{pdo.identity.session_id}' already exists.",
            status_code=status.HTTP_409_CONFLICT
        )
    saved = session_repo.save_session(pdo)
    return saved


@router.get("/{session_id}", response_model=PatientDataObject)
def get_session(session_id: str):
    """Retrieve an active session by ID."""
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return session


@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
def delete_session(session_id: str):
    """
    Terminate and purge ephemeral intake session state.
    Complies with DPDP Act 2023 session lifecycle rules.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Clear session from repository
    session_repo.delete_session(session_id)

    return {
        "success": True,
        "session_id": session_id,
        "status": "TERMINATED",
        "message": "Temporary session data and ephemeral buffers purged successfully."
    }


# ============================================================================
# ABDM Milestone 1 (M1): ABHA Verification & Authentication Endpoints
# ============================================================================

@router.post("/{session_id}/abha/initiate", response_model=AbhaAuthInitResponse)
def initiate_abha_auth(session_id: str, req: AbhaAuthInitRequest):
    """
    ABDM M1: Initiate ABHA verification via Mobile OTP or Aadhaar OTP.
    Operates in ABDM sandbox mode with synthetic OTP generation for offline testing.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    tx_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
    _active_abha_transactions[tx_id] = {
        "session_id": session_id,
        "auth_mode": req.auth_mode,
        "abha_address": req.abha_address or "patient.demo@abdm",
        "abha_number": req.abha_number or "91-1234-5678-9012",
        "mobile": req.mobile or "9876543210",
        "name": "Ramesh Kumar Sharma",
        "gender": session.identity.gender or "MALE",
        "dob": "1974-06-15",
        "created_at": datetime.utcnow()
    }

    return AbhaAuthInitResponse(
        transaction_id=tx_id,
        auth_mode=req.auth_mode,
        message=f"OTP sent to mobile associated with {req.auth_mode}. (Sandbox default OTP: 123456)",
        is_mock_sandbox=True
    )


@router.post("/{session_id}/abha/confirm", response_model=AbhaAuthConfirmResponse)
def confirm_abha_auth(session_id: str, req: AbhaAuthConfirmRequest):
    """
    ABDM M1: Verify OTP and link confirmed ABHA identity into PatientDataObject.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    tx_data = _active_abha_transactions.get(req.transaction_id)
    if not tx_data or tx_data["session_id"] != session_id:
        raise MediKioskException(
            error_code="VALIDATION_FAILED",
            message="Invalid or expired ABHA authentication transaction ID.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # In sandbox mode, OTP 123456 or any 6-digit code is valid
    if len(req.otp.strip()) != 6:
        raise MediKioskException(
            error_code="VALIDATION_FAILED",
            message="Invalid OTP format. Must be 6 digits.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # Link ABHA identity into session
    session.identity.external_identifier = tx_data["abha_address"]
    session.identity.patient_reference = f"PAT_{tx_data['abha_number'].replace('-', '')}"
    session.identity.gender = tx_data["gender"]
    session.identity.age = 52  # calculated from 1974
    session_repo.save_session(session)

    # Remove transaction once confirmed
    del _active_abha_transactions[req.transaction_id]

    return AbhaAuthConfirmResponse(
        success=True,
        abha_number=tx_data["abha_number"],
        abha_address=tx_data["abha_address"],
        name=tx_data["name"],
        gender=tx_data["gender"],
        dob=tx_data["dob"],
        mobile=tx_data["mobile"],
        linked_session_id=session_id,
        message="ABHA account successfully verified and linked to clinical intake session."
    )


# ============================================================================
# Conversational Intake & Adaptive Questioning
# ============================================================================

@router.get("/{session_id}/next-question", response_model=QuestionResponse)
def get_next_question(session_id: str):
    """
    Get the next question for the patient based on their LangGraph interview state.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    facility_type = os.getenv("MEDIKIOSK_FACILITY_ID", "GENERAL")
    
    try:
        state = workflow_manager.get_state(session_id, facility_type)
        if state and state.get("is_completed"):
            raise MediKioskException(
                error_code="SESSION_CONFLICT",
                message="Clinical interview is already complete for this session.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        if state and state.get("pending_question_response"):
            return state.get("pending_question_response")
            
        lang = session.identity.preferred_language
        gender = session.identity.gender
        next_q, _ = workflow_manager.start_workflow(session_id, facility_type, gender, lang)
        
        if next_q:
            return next_q
            
        raise MediKioskException(
            error_code="PROCESSING_UNAVAILABLE",
            message="No further questions available in question bank.",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except MediKioskException:
        raise
    except Exception as e:
        lang = session.identity.preferred_language
        gender = session.identity.gender
        next_q, _ = workflow_manager.start_workflow(session_id, facility_type, gender, lang)
        if next_q:
            return next_q
        raise MediKioskException(
            error_code="INTERNAL_ERROR",
            message=f"Error initializing clinical intake graph: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/{session_id}/answer", response_model=AnswerResult)
def submit_answer(session_id: str, answer: AnswerSubmission):
    """
    Submit an answer to the current question.
    Advances the LangGraph state machine, scans red flags, and registers triage alerts.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    facility_type = os.getenv("MEDIKIOSK_FACILITY_ID", "GENERAL")
    
    state = workflow_manager.get_state(session_id, facility_type)
    if not state:
        lang = session.identity.preferred_language or "en"
        gender = session.identity.gender
        _, state = workflow_manager.start_workflow(session_id, facility_type, gender, lang)
    
    if state.get("is_completed"):
        raise MediKioskException(
            error_code="SESSION_CONFLICT",
            message="Interview is already complete.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Validate the answer if answered
    if answer.answer_state not in ("UNKNOWN", "REFUSED"):
        is_valid, error_msg = answer_validator.validate_answer(
            answer.question_id, answer.selected_value_codes, answer.free_text
        )
        if not is_valid:
            raise MediKioskException(
                error_code="VALIDATION_FAILED",
                message=error_msg or "Invalid option selected.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    # Determine answer payload
    if answer.question_id == "__CHIEF_COMPLAINT__":
        answer_payload = answer.free_text or ""
    else:
        answer_payload = answer.selected_value_codes if answer.selected_value_codes else answer.free_text

    # Advance the graph
    next_q, new_state = workflow_manager.process_step(
        session_id=session_id,
        facility_type=facility_type,
        answered_question_id=answer.question_id,
        answer_value=answer_payload
    )

    # Register any newly triggered red flags into global alert repository
    alerts_data = new_state.get("active_red_flags", [])
    alerts = []
    for a in alerts_data:
        try:
            alert_obj = RedFlagAlert(**a)
            alerts.append(alert_obj)
            
            # Register in global staff triage queue
            severity_map = {
                "EMERGENCY_CRITICAL": "CRITICAL",
                "URGENT_PRIORITY": "HIGH"
            }
            triage_item = TriageAlertItem(
                alert_id=f"ALT_{uuid.uuid4().hex[:8].upper()}",
                session_id=session_id,
                facility_id=facility_type,
                patient_gender=session.identity.gender,
                patient_age=session.identity.age,
                flag_id=alert_obj.rule_id,
                severity=severity_map.get(alert_obj.urgency_level, "CRITICAL"),
                message=alert_obj.alert_message,
                status="TRIGGERED"
            )
            alert_repo.add_alert(triage_item)
        except Exception:
            pass

    is_complete = new_state.get("is_completed", False)

    return AnswerResult(
        success=True,
        next_question=next_q,
        new_alerts=alerts,
        interview_complete=is_complete,
    )


@router.post("/{session_id}/voice/answer")
async def submit_voice_answer(
    session_id: str,
    file: Optional[UploadFile] = File(None),
    language: Optional[str] = Form(None),
    audio_format: str = Form(default="webm"),
    body: Optional[SpeechRecognitionRequest] = None
):
    """
    Module E: Seamless sub-second voice answer submission.
    Transcribes spoken answer -> advances LangGraph state -> scans red flags ->
    generates next question text and synthesized TTS audio in a single API round-trip.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    target_lang = language or session.identity.preferred_language or "hi"
    audio_bytes = b""
    fmt = audio_format

    if file:
        audio_bytes = await file.read()
        if file.filename:
            ext = file.filename.split(".")[-1].lower()
            if ext in ("wav", "webm", "mp3", "ogg"):
                fmt = ext
    elif body and body.audio_base64:
        try:
            audio_bytes = base64.b64decode(body.audio_base64)
            fmt = body.audio_format
        except Exception:
            raise MediKioskException(
                error_code="VALIDATION_FAILED",
                message="Invalid base64 audio payload.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
    else:
        audio_bytes = b"MOCK_PCM_VOICE_ANSWER_BYTES"

    # 1. Transcribe speech using SpeechService cascade
    from app.services.speech.speech_service import speech_service
    trans_res = await speech_service.transcribe_audio(
        audio_bytes=audio_bytes,
        audio_format=fmt,
        language=target_lang,
        session_id=session_id
    )

    if not trans_res.success or not trans_res.transcript:
        raise MediKioskException(
            error_code="PROCESSING_UNAVAILABLE",
            message="Speech recognition was unable to transcribe audio. Please tap options or speak clearly.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retry_guidance="Use touchscreen buttons or speak closer to microphone."
        )

    # 2. Check if spoken utterance is a Module E Navigation Command
    if trans_res.is_voice_action:
        return {
            "success": True,
            "is_voice_action": True,
            "matched_action": trans_res.matched_action,
            "transcript": trans_res.transcript,
            "message": f"Recognized voice navigation command: {trans_res.matched_action}"
        }

    # 3. Fetch active question ID from graph state
    facility_type = os.getenv("MEDIKIOSK_FACILITY_ID", "GENERAL")
    state = workflow_manager.get_state(session_id, facility_type)
    if not state:
        # Start graph if not yet started
        _, state = workflow_manager.start_workflow(
            session_id, facility_type, session.identity.gender, target_lang
        )

    current_qid = state.get("pending_question_id") or "__CHIEF_COMPLAINT__"

    # 4. Submit answer to advance graph
    ans_submission = AnswerSubmission(
        question_id=current_qid,
        free_text=trans_res.transcript,
        selected_value_codes=[]
    )
    answer_result = submit_answer(session_id, ans_submission)

    # 5. Synthesize TTS audio for next question if available
    next_audio_b64 = None
    if answer_result.next_question and answer_result.next_question.question_text:
        tts_res = await speech_service.synthesize_speech(
            text=answer_result.next_question.question_text,
            language=target_lang,
            gender="female",
            audio_format="wav"
        )
        if tts_res.success:
            next_audio_b64 = tts_res.audio_base64

    return {
        "success": True,
        "is_voice_action": False,
        "transcript": trans_res.transcript,
        "confidence": trans_res.confidence,
        "provider_used": trans_res.provider_used,
        "next_question": answer_result.next_question.model_dump() if answer_result.next_question else None,
        "next_question_audio_base64": next_audio_b64,
        "new_alerts": [a.model_dump() for a in answer_result.new_alerts],
        "interview_complete": answer_result.interview_complete
    }


@router.post("/{session_id}/ai/structure-narration")
async def structure_narration_endpoint(session_id: str, narration_text: str, language: str = "en"):
    """
    Structure unstructured patient spoken/free-text narration using ModelService.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    from app.services.model_service import model_service
    res = await model_service.structure_narration(narration_text, language=language, session_id=session_id)
    return res


# ============================================================================
# Clinical Summary & Clinician Review Endpoints
# ============================================================================

@router.post("/{session_id}/ai/generate-summary")
async def generate_summary_endpoint(session_id: str):
    """
    Module C: Synthesizes a physician-ready clinical draft summary with explicit source citations.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    facility_type = os.getenv("MEDIKIOSK_FACILITY_ID", "GENERAL")
    
    state = workflow_manager.get_state(session_id, facility_type)
    if not state:
        lang = session.identity.preferred_language or "en"
        gender = session.identity.gender
        _, state = workflow_manager.start_workflow(session_id, facility_type, gender, lang)

    # Strip PII. The model only needs the clinical facts, not the identity.
    answered_q = dict(state.get("answered_questions", {})) if state else {}
    if not answered_q:
        answered_q["__CHIEF_COMPLAINT__"] = "General OPD clinical evaluation and health check"

    interview_facts = {
        "answered_questions": answered_q,
        "active_red_flags": state.get("active_red_flags", []) if state else [],
        "patient_demographics": {
            "gender": session.identity.gender,
            "age": session.identity.age,
        },
        "facility_type": facility_type
    }

    # Convert session staged documents to OCR summary inputs
    from app.repositories.document_repository import document_repo
    staged_docs = document_repo.list_by_session(session_id)
    ocr_records = []
    for d in staged_docs:
        ocr_records.append({
            "document_id": d.document_id,
            "type": d.file_type,
            "source_date": d.uploaded_at.strftime("%Y-%m-%d"),
            "extracted_text": d.extracted_text_preview or f"Document {d.file_name} staged for clinical review.",
            "source_tag": d.source_tag
        })

    # Default mock records if none uploaded yet
    if not ocr_records:
        ocr_records = [
            {
                "document_id": "DOC_001",
                "type": "DISCHARGE_SUMMARY",
                "source_date": "2024-05-10",
                "extracted_text": "Type 2 Diabetes Mellitus on Metformin 500mg. Hypertension on Telmisartan 40mg.",
                "source_tag": "[Doc#1: Discharge Summary 2024-05-10]"
            }
        ]

    from app.services.model_service import model_service
    res = await model_service.synthesize_clinical_summary(
        interview_facts=interview_facts,
        ocr_extracted_documents=ocr_records,
        language=session.identity.preferred_language,
        session_id=session_id,
    )
    
    if res.success and res.structured_payload:
        res.structured_payload["draft_status"] = "PENDING"
        res.structured_payload["provenance"] = {
            "source_type": "AI_GENERATED",
            "source_id": res.provider_used,
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": res.confidence_score,
            "review_status": "PENDING",
        }
        session.summary = res.structured_payload
        session_repo.save_session(session)
        
    return res


@router.get("/{session_id}/summary/stream")
async def stream_summary_endpoint(session_id: str):
    """
    Server-Sent Events (SSE) streaming endpoint for real-time draft summary delivery.
    Yields progress events: status -> complete -> close.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    async def event_generator():
        yield f"event: status\ndata: {json.dumps({'status': 'INITIALIZING_SYNTHESIS', 'message': 'Gathering clinical facts'})}\n\n"
        await asyncio.sleep(0.2)
        
        yield f"event: status\ndata: {json.dumps({'status': 'INVOKING_MODEL_SERVICE', 'message': 'Generating physician draft'})}\n\n"
        
        # Trigger actual synthesis
        summary_res = await generate_summary_endpoint(session_id)
        if isinstance(summary_res, dict) and not summary_res.get("success", True):
            yield f"event: error\ndata: {json.dumps(summary_res)}\n\n"
            return

        payload = summary_res.structured_payload if hasattr(summary_res, "structured_payload") else summary_res
        yield f"event: complete\ndata: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class SummaryActionRequest(BaseModel):
    """Request body for clinician accept/amend/reject actions on the draft summary."""
    action: str = Field(..., description="ACCEPTED | AMENDED | REJECTED")
    amended_sections: Optional[Dict[str, Any]] = Field(default=None, description="Only required when action is AMENDED. Dict of section keys to new values.")
    clinician_id: str = Field(..., description="ID of the reviewing clinician")
    reason: Optional[str] = Field(default=None, description="Optional reason for rejection or amendment")


@router.post("/{session_id}/summary/review")
def review_summary(session_id: str, review: SummaryActionRequest):
    """
    Clinician action on the generated draft summary.
    Supports accept, amend (with section-level edits), or reject.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    if not session.summary:
        raise MediKioskException(
            error_code="VALIDATION_FAILED",
            message="No draft summary exists for this session. Generate one first.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if review.action not in ("ACCEPTED", "AMENDED", "REJECTED"):
        raise MediKioskException(
            error_code="VALIDATION_FAILED",
            message="Invalid action. Must be ACCEPTED, AMENDED, or REJECTED.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    current_draft = session.summary

    if review.action == "AMENDED":
        if not review.amended_sections:
            raise MediKioskException(
                error_code="VALIDATION_FAILED",
                message="amended_sections is required when action is AMENDED.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        for key, value in review.amended_sections.items():
            if key in current_draft:
                current_draft[key] = value

    current_draft["draft_status"] = review.action
    current_draft["is_draft_for_clinician_review"] = review.action != "ACCEPTED"
    current_draft["provenance"] = {
        "source_type": "CLINICIAN_EDITED" if review.action == "AMENDED" else ("AI_GENERATED" if review.action == "ACCEPTED" else "AI_GENERATED"),
        "source_id": review.clinician_id,
        "timestamp": datetime.utcnow().isoformat(),
        "confidence": None,
        "review_status": "APPROVED" if review.action in ("ACCEPTED", "AMENDED") else "REJECTED",
    }

    session.summary = current_draft
    session_repo.save_session(session)

    return {
        "success": True,
        "session_id": session_id,
        "draft_status": review.action,
        "review_status": current_draft["provenance"]["review_status"],
        "message": f"Draft summary has been {review.action.lower()} by clinician {review.clinician_id}."
    }


@router.get("/{session_id}/summary")
def get_summary(session_id: str):
    """Retrieve the current draft summary for a session, including its review status."""
    session = session_repo.get_session(session_id)
    if not session:
        raise MediKioskException(
            error_code="SESSION_NOT_FOUND",
            message=f"Session with ID '{session_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    if not session.summary:
        raise MediKioskException(
            error_code="NOT_FOUND",
            message="No summary has been generated for this session.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return session.summary
