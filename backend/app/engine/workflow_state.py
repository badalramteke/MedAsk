"""
ClinicalInterviewState: The canonical LangGraph state schema for the clinical interview workflow.
Used as the TypedDict state for StateGraph nodes and edges.
"""
from typing import TypedDict, Optional, List, Dict, Any


class ClinicalInterviewState(TypedDict, total=False):
    """
    Central state object flowing through the LangGraph clinical interview graph.
    Each node reads this state and returns a partial update dict.
    """
    # Session identity
    session_id: str
    facility_type: str  # "GENERAL" or "AYUSH"
    patient_gender: Optional[str]  # "MALE", "FEMALE", or None
    preferred_language: str  # e.g., "en", "hi", "mr"

    # Current position in graph
    current_step: str  # Name of the active node

    # Chief complaint and symptom routing
    chief_complaint: Optional[str]
    active_symptom_domain: Optional[str]  # e.g., "chest_pain", "headache"

    # Accumulated answers (mirrors Phase 2 answer_history)
    answered_questions: Dict[str, Any]  # question_id -> value_codes or free_text

    # Next question to present to the patient
    pending_question_id: Optional[str]
    pending_question_response: Optional[Dict[str, Any]]  # Serialized QuestionResponse

    # Section completion flags
    chief_complaint_recorded: bool
    socrates_completed: bool
    general_history_completed: bool
    menstrual_completed: bool
    ayush_completed: bool

    # Red-flag alerts (non-blocking, accumulated)
    active_red_flags: List[Dict[str, Any]]

    # Clinical validation
    validation_issues: List[str]

    # Overall completion
    is_completed: bool
