"""
General History Node: Sequences through general intake questions
(PMH, PSH, Medications, Allergies, Family, Social History).
Per CLINICAL_PROTOCOLS.md: Required domains include past medical/surgical,
medication/allergy, family, personal, and review-of-systems information.
"""
from typing import Dict, Any, Optional, List
from app.engine.question_bank import question_bank


def _build_question_dict(question_id: str, language: str, phase: str = "GENERAL_HISTORY") -> Optional[Dict[str, Any]]:
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
        "phase": phase,
        "progress_percent": None,
    }


def general_history_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Iterates through general history questions.
    
    Behavior:
    - Gets all general intake question IDs from question_bank.
    - Skips questions with gender restrictions that don't match patient.
    - Skips menstrual history questions (handled by dedicated menstrual node).
    - Finds next unanswered question or marks general_history_completed.
    """
    language = state.get("preferred_language", "en")
    answered = state.get("answered_questions", {})
    gender = state.get("patient_gender")

    # Collect all general intake question IDs in order
    all_general_qids: List[str] = []
    for section_ids in question_bank._general_sections.values():
        all_general_qids.extend(section_ids)

    # Find the next unanswered question
    for qid in all_general_qids:
        if qid in answered:
            continue

        # Skip menstrual history questions — handled by menstrual_history_node
        if qid.startswith("GEN_MEN_"):
            continue

        # Check gender restriction
        q_data = question_bank.get_question(qid)
        if q_data:
            restriction = q_data.get("gender_restriction")
            if restriction == "FEMALE" and gender and gender.upper() != "FEMALE":
                continue

        question_dict = _build_question_dict(qid, language)
        if question_dict:
            return {
                "current_step": "general_history",
                "pending_question_id": qid,
                "pending_question_response": question_dict,
            }

    # All general history questions answered
    return {
        "current_step": "general_history",
        "general_history_completed": True,
        "pending_question_id": None,
        "pending_question_response": None,
    }
