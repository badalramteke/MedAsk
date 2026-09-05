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


# Map of detail question IDs to their parent screening question ID and negative code
PARENT_DETAIL_MAP = {
    "GEN_PMH_002": ("GEN_PMH_001", "PMH_NO"),
    "GEN_PSH_002": ("GEN_PSH_001", "PSH_NO"),
    "GEN_MED_002": ("GEN_MED_001", "MED_NO"),
    "GEN_ALG_002": ("GEN_ALG_001", "ALG_NO"),
    "GEN_FH_002": ("GEN_FH_001", "FH_NO"),
    "GEN_SH_002": ("GEN_SH_001", "SH_NO"),
}

NEGATIVE_VALUE_CODES = {
    "SH_NO", "FH_NO", "MED_NO", "ALG_NO", "PMH_NO", "PSH_NO", "MEN_NOT_APPLICABLE"
}


def is_negative_response(ans: Any, expected_no_code: str = "") -> bool:
    """Detect if an answer represents a negative response (No, None, Do not take, etc.)."""
    if not ans:
        return False

    if isinstance(ans, list):
        if expected_no_code and expected_no_code in ans:
            return True
        for item in ans:
            if str(item).endswith("_NO") or str(item) in NEGATIVE_VALUE_CODES:
                return True
        # Check text in list items if any
        ans_str = " ".join(str(x) for x in ans)
    else:
        ans_str = str(ans)

    text = ans_str.strip().lower()
    if expected_no_code and expected_no_code.lower() in text:
        return True

    words = text.replace(".", " ").replace(",", " ").replace("-", " ").split()
    if any(w in {"no", "none", "never", "not", "dont", "nahi", "na", "nil"} for w in words):
        return True

    negative_phrases = [
        "do not", "don't", "kuch nahi", "nahi leta", "nahi lete", "nahi leti",
        "nahi pta", "pta nahi", "no substances", "no drugs", "no alcohol",
        "no tobacco", "not taking", "no known", "no medical", "no allergies"
    ]
    if any(phrase in text for phrase in negative_phrases):
        return True

    return False


def general_history_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Iterates through general history questions with dynamic branching.
    
    Behavior:
    - Sequences through general intake questions (PMH, PSH, Meds, Allergies, Family, Social).
    - Checks parent answers: if patient answered negatively (e.g. 'No' or 'Do not take substances'),
      automatically skips the detailed follow-up inquiry.
    - Skips questions with gender restrictions that don't match patient.
    - Skips menstrual history questions (handled by dedicated menstrual node).
    - Finds next valid unanswered question or marks general_history_completed.
    """
    language = state.get("preferred_language", "en")
    answered = state.get("answered_questions", {})
    gender = state.get("patient_gender")

    # Collect all general intake question IDs in order
    all_general_qids: List[str] = []
    for section_ids in question_bank._general_sections.values():
        all_general_qids.extend(section_ids)

    # Find the next unanswered question respecting conditional triggers
    for qid in all_general_qids:
        if qid in answered:
            continue

        # Skip menstrual history questions — handled by menstrual_history_node
        if qid.startswith("GEN_MEN_"):
            continue

        # Check conditional dependency on parent screening question
        if qid in PARENT_DETAIL_MAP:
            parent_qid, no_code = PARENT_DETAIL_MAP[qid]
            if parent_qid not in answered:
                # Parent hasn't been asked yet; ask parent first
                continue
            
            parent_answer = answered.get(parent_qid)
            if is_negative_response(parent_answer, no_code):
                # Patient stated absence of condition/substance -> skip detail question!
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
