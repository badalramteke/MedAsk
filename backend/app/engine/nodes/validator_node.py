"""
Validator Node: Deterministic completeness checker for the clinical interview.
Per QUESTION_ENGINE_SPEC.md: Checks each applicable field has an answer,
explicit refusal/unknown, or clinician-review-required gap.
Per CLINICAL_SAFETY.md: Preserves uncertainty and contradictions for clinician review;
never silently infers a diagnosis.
"""
from typing import Dict, Any, List


def validator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Validates interview completeness before marking is_completed.
    
    Checks:
    1. Chief complaint is recorded.
    2. SOCRATES questions completed (or skipped for non-matching complaints).
    3. General history completed.
    4. Menstrual history completed (or skipped for non-female).
    5. AYUSH completed (or skipped for non-AYUSH facility).
    
    Returns validation_issues list and is_completed flag.
    """
    issues: List[str] = []
    
    # Check chief complaint
    if not state.get("chief_complaint_recorded", False):
        issues.append("Chief complaint not yet recorded.")
    
    if not state.get("chief_complaint"):
        issues.append("Chief complaint text is empty.")
    
    # Check SOCRATES completion
    if not state.get("socrates_completed", False):
        issues.append("SOCRATES deep-dive not completed for matched symptom domain.")
    
    # Check general history completion
    if not state.get("general_history_completed", False):
        issues.append("General history intake not completed.")
    
    # Check menstrual history (only for female patients)
    gender = state.get("patient_gender")
    if gender and gender.upper() == "FEMALE":
        if not state.get("menstrual_completed", False):
            issues.append("Menstrual/reproductive history not completed for female patient.")
    
    # Check AYUSH completion (only for AYUSH facilities)
    facility_type = state.get("facility_type", "GENERAL")
    if facility_type.upper() == "AYUSH":
        if not state.get("ayush_completed", False):
            issues.append("AYUSH Dashavidha Pariksha not completed for AYUSH facility.")
    
    is_completed = len(issues) == 0
    
    return {
        "current_step": "validator",
        "validation_issues": issues,
        "is_completed": is_completed,
    }
