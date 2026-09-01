"""
Chief Complaint Node: Captures and routes the patient's chief complaint.
If the complaint matches a known SOCRATES domain, routes to SOCRATES deep-dive.
Otherwise, routes to general history (or AYUSH if facility is AYUSH).
"""
from typing import Dict, Any
from app.engine.question_bank import question_bank

# Known chief complaint -> SOCRATES domain mappings
# Reused from Phase 2 flow_controller.py for consistency
CHIEF_COMPLAINT_TO_DOMAIN = {
    "chest_pain": "chest_pain",
    "chest pain": "chest_pain",
    "headache": "headache",
    "head pain": "headache",
    "sir dard": "headache",
    "seene mein dard": "chest_pain",
}


def _localize_chief_complaint_prompt(language: str) -> str:
    """Return the chief complaint prompt in the patient's preferred language."""
    prompts = {
        "en": "What is your main health problem or complaint today?",
        "hi": "आज आपकी मुख्य स्वास्थ्य समस्या या शिकायत क्या है?",
        "mr": "आज तुमची मुख्य आरोग्य समस्या किंवा तक्रार काय आहे?",
        "bn": "আজ আপনার প্রধান স্বাস্থ্য সমস্যা বা অভিযোগ কী?",
        "ta": "இன்று உங்கள் முக்கிய உடல்நலப் பிரச்சனை அல்லது புகார் என்ன?",
        "te": "ఈ రోజు మీ ప్రధాన ఆరోగ్య సమస్య లేదా ఫిర్యాదు ఏమిటి?",
    }
    return prompts.get(language, prompts["en"])


def chief_complaint_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Handles the chief complaint capture phase.
    
    Behavior:
    - If chief complaint is NOT yet recorded: returns the CC prompt question.
    - If chief complaint IS recorded: determines SOCRATES domain and sets routing flags.
    """
    language = state.get("preferred_language", "en")
    
    # If chief complaint is not yet captured, present the prompt
    if not state.get("chief_complaint_recorded", False):
        return {
            "current_step": "chief_complaint",
            "pending_question_id": "__CHIEF_COMPLAINT__",
            "pending_question_response": {
                "question_id": "__CHIEF_COMPLAINT__",
                "question_text": _localize_chief_complaint_prompt(language),
                "input_type": "free_text",
                "options": [],
                "data_element": "history.chief_complaint",
                "phase": "CHIEF_COMPLAINT",
                "progress_percent": 0.0,
            },
            "chief_complaint_recorded": False,
        }

    # Chief complaint already recorded — determine SOCRATES routing
    complaint_text = state.get("chief_complaint", "")
    complaint_lower = complaint_text.strip().lower() if complaint_text else ""
    
    domain = CHIEF_COMPLAINT_TO_DOMAIN.get(complaint_lower)
    print("CHIEF COMPLAINT DOMAIN MATCHED:", domain)
    if domain and question_bank.has_socrates_domain(domain):
        print("RETURNING ACTIVE DOMAIN:", domain)
        return {
            "current_step": "chief_complaint",
            "active_symptom_domain": domain,
            "chief_complaint_recorded": True,
        }

    # No SOCRATES match — skip SOCRATES, mark as done
    print("NO SOCRATES MATCH, RETURNING None")
    return {
        "current_step": "chief_complaint",
        "active_symptom_domain": None,
        "socrates_completed": True,
        "chief_complaint_recorded": True,
    }
