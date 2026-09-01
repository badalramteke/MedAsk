"""
AYUSH Node: Sequences through Dashavidha Pariksha parameters for AYUSH facility deployments.
Per DASHAVIDHA_PARIKSHA.md:
  - 10 parameters to capture (Prakriti, Vikriti, Sara, Samhanana, Pramana, Satmya, Sattva,
    Ahara Shakti, Vyayama Shakti, Vaya).
  - "Does not define treatment, diagnosis, scoring, interpretation."
  - AYUSH clinician approval pending for question bank, terminology translations.

This node only activates when facility_type == "AYUSH".
Ahara-Vihara assessment is a structural placeholder — no fabricated questions.
"""
from typing import Dict, Any, Optional, List
from app.engine.question_bank import question_bank


def _build_ayush_question_dict(parameter: dict, language: str) -> Optional[Dict[str, Any]]:
    """Build a serializable question response dict from an AYUSH parameter entry."""
    param_id = parameter.get("parameter_id", "")
    text_by_lang = parameter.get("text_by_language", {})
    question_text = text_by_lang.get(language, text_by_lang.get("en", ""))
    
    options = []
    for opt in parameter.get("options", []):
        opt_text_by_lang = opt.get("text_by_language", {})
        options.append({
            "option_id": opt.get("option_id", ""),
            "value_code": opt.get("value_code", ""),
            "text": opt_text_by_lang.get(language, opt_text_by_lang.get("en", "")),
        })

    return {
        "question_id": param_id,
        "question_text": question_text,
        "input_type": parameter.get("input_type", "single_select"),
        "options": options,
        "data_element": f"ayush.dashavidha.{parameter.get('sanskrit_name', '').lower()}",
        "phase": "AYUSH_DASHAVIDHA",
        "progress_percent": None,
    }


def ayush_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Sequences through Dashavidha Pariksha parameters.
    
    Behavior:
    - Only activates when facility_type == "AYUSH".
    - Iterates through all 10 Dashavidha parameters from question_bank.
    - Returns the next unanswered parameter question or marks ayush_completed.
    - Ahara-Vihara is logged as a placeholder — pending dataset creation.
    """
    facility_type = state.get("facility_type", "GENERAL")
    language = state.get("preferred_language", "en")
    answered = state.get("answered_questions", {})

    # Skip for non-AYUSH facilities
    if facility_type.upper() != "AYUSH":
        return {
            "current_step": "ayush",
            "ayush_completed": True,
            "pending_question_id": None,
            "pending_question_response": None,
        }

    # Get AYUSH parameters from question_bank
    ayush_params = question_bank.get_ayush_parameters()
    
    # Find the next unanswered parameter
    for param in ayush_params:
        param_id = param.get("parameter_id", "")
        if param_id and param_id not in answered:
            question_dict = _build_ayush_question_dict(param, language)
            if question_dict:
                return {
                    "current_step": "ayush",
                    "pending_question_id": param_id,
                    "pending_question_response": question_dict,
                }

    # All AYUSH parameters answered
    # NOTE: Ahara-Vihara assessment is a structural placeholder.
    # Per DASHAVIDHA_PARIKSHA.md, the dataset for Ahara-Vihara is pending clinician approval.
    return {
        "current_step": "ayush",
        "ayush_completed": True,
        "pending_question_id": None,
        "pending_question_response": None,
    }
