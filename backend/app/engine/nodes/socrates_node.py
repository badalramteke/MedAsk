"""
SOCRATES Node: Iterates through SOCRATES symptom-probing questions for a matched domain.
Per SOCRATES_FRAMEWORK.md: 8 structured elements (Site, Onset, Character, Radiation,
Associated, Timing, Exacerbating/Relieving, Severity).
Does NOT diagnose — only structures symptom history for clinician review.
"""
from typing import Dict, Any, Optional
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
        "phase": "SOCRATES_DEEP_DIVE",
        "progress_percent": None,  # Calculated by the workflow manager
    }


def socrates_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Iterates through SOCRATES questions for the active symptom domain.
    
    Behavior:
    - Looks up the active_symptom_domain (e.g., 'chest_pain', 'headache').
    - Finds the next unanswered SOCRATES question in that domain.
    - Returns the question or marks socrates_completed=True if all done.
    """
    domain = state.get("active_symptom_domain")
    language = state.get("preferred_language", "en")
    answered = state.get("answered_questions", {})

    # If no domain is set, SOCRATES is not applicable
    if not domain:
        return {
            "current_step": "socrates",
            "socrates_completed": True,
        }

    # Get ordered question IDs for this SOCRATES domain
    domain_question_ids = question_bank._socrates_domains.get(domain, [])
    
    # Find the next unanswered question
    for qid in domain_question_ids:
        if qid not in answered:
            question_dict = _build_question_dict(qid, language)
            if question_dict:
                return {
                    "current_step": "socrates",
                    "pending_question_id": qid,
                    "pending_question_response": question_dict,
                }

    # All SOCRATES questions for this domain answered
    return {
        "current_step": "socrates",
        "socrates_completed": True,
        "pending_question_id": None,
        "pending_question_response": None,
    }
