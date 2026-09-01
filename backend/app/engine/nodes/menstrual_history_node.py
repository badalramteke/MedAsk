"""
Menstrual History Node: Activated only when patient_gender == "FEMALE".
Per CLINICAL_PROTOCOLS.md: "Reproductive history — Ask only when the patient
identifies as female and the clinician-approved flow applies."
"""
from typing import Dict, Any, Optional, List
from app.engine.question_bank import question_bank


def _build_question_dict(question_id: str, language: str) -> Optional[Dict[str, Any]]:
    """Build a serializable question response dict from question_bank data."""
    localized = question_bank.localize_question(question_id, language)
    if not localized:
        return None
    return {
        "question_id": localized["question_id"],
        "question_text": localized["question_text"],
        "input_type": localized["input_type"],
        "options": localized["options"],
        "data_element": localized.get("data_element"),
        "phase": "MENSTRUAL_HISTORY",
        "progress_percent": None,
    }


# Known menstrual history question IDs from questions_general_intake.json
MENSTRUAL_QUESTION_IDS = ["GEN_MEN_001", "GEN_MEN_002"]


def menstrual_history_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Captures menstrual/reproductive history for female patients.
    
    Behavior:
    - Only activates when patient_gender == "FEMALE".
    - Sequences through GEN_MEN_001, GEN_MEN_002 from question_bank.
    - Non-female patients skip immediately.
    """
    gender = state.get("patient_gender")
    language = state.get("preferred_language", "en")
    answered = state.get("answered_questions", {})

    # Skip for non-female patients
    if not gender or gender.upper() != "FEMALE":
        return {
            "current_step": "menstrual_history",
            "menstrual_completed": True,
            "pending_question_id": None,
            "pending_question_response": None,
        }

    # Find the next unanswered menstrual question
    for qid in MENSTRUAL_QUESTION_IDS:
        if qid not in answered:
            question_dict = _build_question_dict(qid, language)
            if question_dict:
                return {
                    "current_step": "menstrual_history",
                    "pending_question_id": qid,
                    "pending_question_response": question_dict,
                }

    # All menstrual questions answered
    return {
        "current_step": "menstrual_history",
        "menstrual_completed": True,
        "pending_question_id": None,
        "pending_question_response": None,
    }
