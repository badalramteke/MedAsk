from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.core import PatientDataObject
from app.models.patch import PatientDataPatch
from app.models.interview import (
    InterviewState, AnswerSubmission, AnswerResult,
    QuestionResponse, RedFlagAlert,
)
from app.repositories.session_repository import session_repo
from app.engine.flow_controller import flow_controller
from app.engine.answer_validator import answer_validator
from app.engine.red_flag_scanner import red_flag_scanner

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
    Get the next question for the patient based on their interview state.
    If the interview hasn't started, returns the chief complaint prompt.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    state = _interview_states.get(session_id)
    if not state:
        state = InterviewState()
        _interview_states[session_id] = state

    lang = session.identity.preferred_language

    if state.is_complete:
        raise HTTPException(status_code=400, detail="Interview is already complete.")

    # If no questions answered yet, return the first question
    if not state.answered_question_ids:
        question = flow_controller.get_first_question(state, lang)
        return question

    # Otherwise return the current question
    if state.current_question_id:
        from app.engine.question_bank import question_bank
        localized = question_bank.localize_question(state.current_question_id, lang)
        if localized:
            from app.models.interview import QuestionOption
            return QuestionResponse(
                question_id=localized["question_id"],
                question_text=localized["question_text"],
                input_type=localized["input_type"],
                options=[
                    QuestionOption(option_id=o["option_id"], value_code=o["value_code"], text=o["text"])
                    for o in localized["options"]
                ],
                data_element=localized.get("data_element"),
                phase=state.current_phase,
            )

    raise HTTPException(status_code=400, detail="No more questions available.")


@router.post("/{session_id}/answer", response_model=AnswerResult)
def submit_answer(session_id: str, answer: AnswerSubmission):
    """
    Submit an answer to the current question.
    Validates the answer, patches PDO, scans for red flags, advances state.
    """
    session = session_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    state = _interview_states.get(session_id)
    if not state:
        raise HTTPException(status_code=400, detail="Interview not started. Call GET /next-question first.")

    if state.is_complete:
        raise HTTPException(status_code=400, detail="Interview is already complete.")

    lang = session.identity.preferred_language

    gender = session.identity.gender

    # Handle UNKNOWN / REFUSED states — skip validation, move forward
    if answer.answer_state in ("UNKNOWN", "REFUSED"):
        next_q = flow_controller.process_answer(
            state, answer.question_id, [], answer.free_text, lang, gender=gender
        )
        return AnswerResult(
            success=True,
            next_question=next_q,
            interview_complete=state.is_complete,
        )

    # Validate the answer
    is_valid, error_msg = answer_validator.validate_answer(
        answer.question_id, answer.selected_value_codes, answer.free_text
    )
    if not is_valid:
        raise HTTPException(status_code=422, detail=error_msg)

    # Special handling for chief complaint
    if answer.question_id == "__CHIEF_COMPLAINT__":
        next_q = flow_controller.process_chief_complaint(state, answer.free_text or "", lang)
    else:
        next_q = flow_controller.process_answer(
            state, answer.question_id, answer.selected_value_codes, answer.free_text, lang, gender=gender
        )

    # Run red flag scan after every answer
    new_alerts = red_flag_scanner.scan(state.answer_history, lang)

    # Store new alerts (deduplicate by rule_id)
    existing_rule_ids = {a.rule_id for a in _session_alerts.get(session_id, [])}
    for alert in new_alerts:
        if alert.rule_id not in existing_rule_ids:
            _session_alerts.setdefault(session_id, []).append(alert)

    unique_new = [a for a in new_alerts if a.rule_id not in existing_rule_ids]

    return AnswerResult(
        success=True,
        next_question=next_q,
        new_alerts=unique_new,
        interview_complete=state.is_complete,
    )


@router.get("/{session_id}/alerts", response_model=List[RedFlagAlert])
def get_alerts(session_id: str):
    """Get all active red-flag alerts for this session."""
    if not session_repo.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    return _session_alerts.get(session_id, [])


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

    state = _interview_states.get(session_id)
    interview_facts = state.answer_history if state else {}

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
        session_id=session_id,
    )
    return res


@router.get("/ai/health")
async def ai_health_status():
    """Diagnostic health check across all AI model providers."""
    from app.services.model_service import model_service
    return await model_service.get_health_status()

