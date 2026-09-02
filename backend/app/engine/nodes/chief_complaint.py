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
    # English
    "chest_pain": "chest_pain",
    "chest pain": "chest_pain",
    "chest": "chest_pain",
    "headache": "headache",
    "head pain": "headache",
    "head": "headache",
    "fever": "fever",
    "cough": "cough",
    # Hindi (Transliterated & Devanagari)
    "sir dard": "headache",
    "seene mein dard": "chest_pain",
    "seene": "chest_pain",
    "सीने में तेज दर्द": "chest_pain",
    "सीने में दर्द": "chest_pain",
    "सीने": "chest_pain",
    "छाती": "chest_pain",
    "सिर दर्द": "headache",
    "सिर": "headache",
    "बुखार": "fever",
    "खांसी": "cough",
    # Marathi
    "छातीत": "chest_pain",
    "डोकेदुखी": "headache",
    "ताप": "fever",
    "खोकला": "cough",
    # Bengali
    "বুকে": "chest_pain",
    "মাথা ব্যথা": "headache",
    "জ্বর": "fever",
    "কাশি": "cough",
    # Tamil
    "நெஞ்சு": "chest_pain",
    "தலைவலி": "headache",
    "காய்ச்சல்": "fever",
    "இருமல்": "cough",
    # Telugu
    "ఛాతీ": "chest_pain",
    "తలనొప్పి": "headache",
    "జ్వరం": "fever",
    "దగ్గు": "cough",
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
    domain = None
    for pattern, matched_domain in CHIEF_COMPLAINT_TO_DOMAIN.items():
        if pattern in complaint_lower:
            domain = matched_domain
            break

    if domain and question_bank.has_socrates_domain(domain):
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
