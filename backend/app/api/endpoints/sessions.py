from fastapi import APIRouter, HTTPException, status, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from pydantic import BaseModel, Field
from app.models.core import PatientDataObject
from app.models.patch import PatientDataPatch
from app.models.interview import (
    InterviewState, AnswerSubmission, AnswerResult,
    QuestionResponse, RedFlagAlert,
)
from app.repositories.session_repository import session_repo
from app.engine.answer_validator import answer_validator
from app.engine.langgraph_workflow import workflow_manager

router = APIRouter()

# In-memory interview states and alerts (keyed by session_id)
_interview_states: dict[str, InterviewState] = {}
_session_alerts: dict[str, list[RedFlagAlert]] = {}


@router.post("/", response_model=PatientDataObject, status_code=status.HTTP_201_CREATED)
def create_session(pdo: PatientDataObject):
    """Create a new clinical intake session."""
    if session_repo.get_session(pdo.identity.session_id):
        raise HTTPException(status_code=400, detail="Session already exists.")
    saved = session_repo.save_session(pdo)
    # Initialize interview state
    _interview_states[pdo.identity.session_id] = InterviewState()
    _session_alerts[pdo.identity.session_id] = []
    return saved


@router.get("/{session_id}", response_model=PatientDataObject)
def get_session(session_id: str):
    """Retrieve an active session by ID."""
    session = session_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


@router.get("/{session_id}/next-question", response_model=QuestionResponse)
def get_next_question(session_id: str):
    """
    Get the next question for the patient based on their LangGraph interview state.
    If the interview hasn't started, initializes the graph and returns the first prompt.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    facility_type = os.getenv("MEDIKIOSK_FACILITY_ID", "GENERAL")
    
    try:
        # Try to fetch existing state
        state = workflow_manager.get_state(session_id, facility_type)
        if state and state.get("is_completed"):
            raise HTTPException(status_code=400, detail="Interview is already complete.")
            
        if state and state.get("pending_question_response"):
            return state.get("pending_question_response")
            
        # If no state or no pending question, initialize workflow
        lang = session.identity.preferred_language
        gender = session.identity.gender
        next_q, _ = workflow_manager.start_workflow(session_id, facility_type, gender, lang)
        
        if next_q:
            return next_q
            
        raise HTTPException(status_code=400, detail="No more questions available.")
    except Exception as e:
        # Fallback if workflow not initialized
        lang = session.identity.preferred_language
        gender = session.identity.gender
        next_q, _ = workflow_manager.start_workflow(session_id, facility_type, gender, lang)
        if next_q:
            return next_q
        raise HTTPException(status_code=400, detail="Error starting workflow: " + str(e))


@router.post("/{session_id}/answer", response_model=AnswerResult)
def submit_answer(session_id: str, answer: AnswerSubmission):
    """
    Submit an answer to the current question.
    Advances the LangGraph state machine and returns the next step.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    facility_type = os.getenv("MEDIKIOSK_FACILITY_ID", "GENERAL")
    
    try:
        state = workflow_manager.get_state(session_id, facility_type)
        if not state:
            raise HTTPException(status_code=400, detail="Interview not started. Call GET /next-question first.")
        
        if state.get("is_completed"):
            raise HTTPException(status_code=400, detail="Interview is already complete.")
            
    except Exception:
        raise HTTPException(status_code=400, detail="Interview not started. Call GET /next-question first.")

    # Handle UNKNOWN / REFUSED states — skip validation
    if answer.answer_state not in ("UNKNOWN", "REFUSED"):
        # Validate the answer
        is_valid, error_msg = answer_validator.validate_answer(
            answer.question_id, answer.selected_value_codes, answer.free_text
        )
        if not is_valid:
            raise HTTPException(status_code=422, detail=error_msg)

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

    # Convert state active_red_flags to Response Models
    # (In a real system, we'd compare before/after state to only return NEW alerts to the frontend)
    # For now, we return all active alerts
    alerts_data = new_state.get("active_red_flags", [])
    alerts = []
    for a in alerts_data:
        try:
            alerts.append(RedFlagAlert(**a))
        except Exception:
            pass # ignore invalid formatted alerts
            
    is_complete = new_state.get("is_completed", False)

    return AnswerResult(
        success=True,
        next_question=next_q,
        new_alerts=alerts,
        interview_complete=is_complete,
    )


@router.get("/{session_id}/alerts", response_model=List[RedFlagAlert])
def get_alerts(session_id: str):
    """Get all active red-flag alerts for this session from LangGraph state."""
    session = session_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    facility_type = os.getenv("MEDIKIOSK_FACILITY_ID", "GENERAL")
    try:
        state = workflow_manager.get_state(session_id, facility_type)
        alerts_data = state.get("active_red_flags", [])
        return [RedFlagAlert(**a) for a in alerts_data]
    except Exception:
        return []



@router.post("/{session_id}/ai/structure-narration")
async def structure_narration_endpoint(session_id: str, narration_text: str, language: str = "en"):
    """
    Structure unstructured patient spoken/free-text narration using ModelService.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    from app.services.model_service import model_service
    res = await model_service.structure_narration(narration_text, language=language, session_id=session_id)
    return res


@router.post("/{session_id}/ai/generate-summary")
async def generate_summary_endpoint(session_id: str):
    """
    Module C: Ingests structured interview facts + source-tagged OCR records
    and synthesizes a physician-ready clinical draft summary with explicit source citations.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    facility_type = os.getenv("MEDIKIOSK_FACILITY_ID", "GENERAL")
    
    try:
        # Fetch the canonical interview state from the graph
        state = workflow_manager.get_state(session_id, facility_type)
        if not state:
            raise HTTPException(status_code=400, detail="Interview not started.")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching interview state: " + str(e))

    # Strip PII. The model only needs the clinical facts, not the identity.
    interview_facts = {
        "answered_questions": state.get("answered_questions", {}),
        "active_red_flags": state.get("active_red_flags", []),
        "patient_demographics": {
            "gender": session.identity.gender,
            "age": session.identity.age,
        },
        "facility_type": facility_type
    }

    # If the user answered nothing (completely empty state)
    if not interview_facts["answered_questions"] and not interview_facts["active_red_flags"]:
        return {
            "success": False,
            "error_message": "Patient declined to provide history. No summary generated."
        }

    # Sample source-tagged OCR records (to be linked with Module B in Phase 8)
    ocr_records = [
        {
            "document_id": "DOC_001",
            "type": "DISCHARGE_SUMMARY",
            "source_date": "2024-05-10",
            "extracted_text": "Known Type 2 Diabetes Mellitus on Metformin 500mg BD. Hypertension on Telmisartan 40mg OD.",
            "source_tag": "[Doc#1: Discharge Summary 2024-05-10]"
        },
        {
            "document_id": "DOC_002",
            "type": "LAB_REPORT",
            "source_date": "2024-05-12",
            "extracted_text": "Fasting Blood Sugar: 142 mg/dL (Ref: 70-100), HbA1c: 7.8% (Ref: <5.7).",
            "source_tag": "[Doc#2: Lab Report 2024-05-12]"
        }
    ]

    from app.services.model_service import model_service
    res = await model_service.synthesize_clinical_summary(
        interview_facts=interview_facts,
        ocr_extracted_documents=ocr_records,
        language=session.identity.preferred_language,
        session_id=session_id,
    )
    
    # Persist the draft in the backend session state for Phase 12 clinician review
    if res.success and res.structured_payload:
        # Attach provenance metadata to the draft
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
    The draft is never committed as a final clinical record without this explicit clinician action.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not session.summary:
        raise HTTPException(status_code=400, detail="No draft summary exists for this session. Generate one first.")

    if review.action not in ("ACCEPTED", "AMENDED", "REJECTED"):
        raise HTTPException(status_code=422, detail="Invalid action. Must be ACCEPTED, AMENDED, or REJECTED.")

    current_draft = session.summary

    if review.action == "AMENDED":
        if not review.amended_sections:
            raise HTTPException(status_code=422, detail="amended_sections is required when action is AMENDED.")
        # Apply section-level patches
        for key, value in review.amended_sections.items():
            if key in current_draft:
                current_draft[key] = value

    # Update draft status and provenance
    current_draft["draft_status"] = review.action
    current_draft["is_draft_for_clinician_review"] = review.action != "ACCEPTED"
    current_draft["provenance"] = {
        "source_type": "CLINICIAN_EDITED" if review.action == "AMENDED" else ("AI_GENERATED" if review.action == "ACCEPTED" else "AI_GENERATED"),
        "source_id": review.clinician_id,
        "timestamp": datetime.utcnow().isoformat(),
        "confidence": None,
        "review_status": "APPROVED" if review.action == "ACCEPTED" else ("APPROVED" if review.action == "AMENDED" else "REJECTED"),
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
        raise HTTPException(status_code=404, detail="Session not found.")
    if not session.summary:
        raise HTTPException(status_code=404, detail="No summary has been generated for this session.")
    return session.summary


@router.get("/ai/health")
async def ai_health_status():
    """Diagnostic health check across all AI model providers."""
    from app.services.model_service import model_service
    return await model_service.get_health_status()

