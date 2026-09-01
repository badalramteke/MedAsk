"""
FlowController: Manages the dynamic interview state machine.
Determines which question to present next based on previous answers.
"""
from typing import Optional, List
from app.models.interview import InterviewState, QuestionResponse, QuestionOption
from app.engine.question_bank import question_bank

# Known chief complaint → SOCRATES domain mappings
CHIEF_COMPLAINT_TO_DOMAIN = {
    "chest_pain": "chest_pain",
    "chest pain": "chest_pain",
    "headache": "headache",
    "head pain": "headache",
    "sir dard": "headache",
    "seene mein dard": "chest_pain",
}


class FlowController:
    """
    Controls the interview flow. Each method takes the current InterviewState
    and returns the next QuestionResponse + updated state.
    """

    def get_first_question(self, state: InterviewState, language: str = "en") -> QuestionResponse:
        """Return the chief complaint entry question."""
        state.current_phase = "CHIEF_COMPLAINT"
        state.current_question_id = "__CHIEF_COMPLAINT__"

        return QuestionResponse(
            question_id="__CHIEF_COMPLAINT__",
            question_text=_localize_chief_complaint_prompt(language),
            input_type="free_text",
            options=[],
            data_element="history.chief_complaint",
            phase="CHIEF_COMPLAINT",
            progress_percent=0.0,
        )

    def process_chief_complaint(
        self, state: InterviewState, complaint_text: str, language: str = "en"
    ) -> Optional[QuestionResponse]:
        """
        After patient states their chief complaint, decide the next branch:
        - If complaint matches a SOCRATES domain → enter SOCRATES deep-dive
        - Otherwise → jump to general history
        """
        complaint_lower = complaint_text.strip().lower()
        state.answered_question_ids.append("__CHIEF_COMPLAINT__")
        state.answer_history["__CHIEF_COMPLAINT__"] = complaint_text

        # Check if complaint maps to a known SOCRATES domain
        domain = CHIEF_COMPLAINT_TO_DOMAIN.get(complaint_lower)
        if domain and question_bank.has_socrates_domain(domain):
            state.current_phase = "SOCRATES_DEEP_DIVE"
            state.active_symptom_domain = domain
            entry_qid = question_bank.get_socrates_entry_question(domain)
            state.current_question_id = entry_qid
            return self._build_question_response(entry_qid, "SOCRATES_DEEP_DIVE", language, state)

        # No SOCRATES match → go to general history
        return self._enter_general_history(state, language)

    def process_answer(
        self,
        state: InterviewState,
        question_id: str,
        selected_value_codes: List[str],
        free_text: Optional[str],
        language: str = "en",
    ) -> Optional[QuestionResponse]:
        """
        Process an answer and return the next question.
        Uses followup_triggers from the JSON data for dynamic branching.
        """
        state.answered_question_ids.append(question_id)
        state.answer_history[question_id] = selected_value_codes if selected_value_codes else free_text

        # Use the question bank's trigger-based routing
        next_qid = question_bank.get_next_question_id(question_id, selected_value_codes)

        if next_qid:
            state.current_question_id = next_qid
            # Determine phase based on question prefix
            phase = self._determine_phase(next_qid, state)
            return self._build_question_response(next_qid, phase, language, state)

        # No next question from triggers — check if we need to transition phases
        if state.current_phase == "SOCRATES_DEEP_DIVE":
            # SOCRATES complete → enter general history
            return self._enter_general_history(state, language)
        
        # Interview is complete
        state.current_phase = "INTERVIEW_COMPLETE"
        state.is_complete = True
        from datetime import datetime
        state.completed_at = datetime.utcnow()
        return None

    def _enter_general_history(self, state: InterviewState, language: str) -> Optional[QuestionResponse]:
        state.current_phase = "GENERAL_HISTORY"
        state.active_symptom_domain = None
        entry_qid = question_bank.get_general_entry_question()
        if entry_qid:
            state.current_question_id = entry_qid
            return self._build_question_response(entry_qid, "GENERAL_HISTORY", language, state)
        # No general questions available
        state.current_phase = "INTERVIEW_COMPLETE"
        state.is_complete = True
        return None

    def _determine_phase(self, question_id: str, state: InterviewState) -> str:
        if question_id.startswith("SOC_"):
            return "SOCRATES_DEEP_DIVE"
        elif question_id.startswith("GEN_"):
            return "GENERAL_HISTORY"
        return state.current_phase

    def _build_question_response(
        self, question_id: str, phase: str, language: str, state: InterviewState
    ) -> Optional[QuestionResponse]:
        localized = question_bank.localize_question(question_id, language)
        if not localized:
            return None

        total_possible = max(len(state.answered_question_ids) + 5, 1)
        progress = min(len(state.answered_question_ids) / total_possible * 100, 95.0)

        return QuestionResponse(
            question_id=localized["question_id"],
            question_text=localized["question_text"],
            input_type=localized["input_type"],
            options=[
                QuestionOption(
                    option_id=opt["option_id"],
                    value_code=opt["value_code"],
                    text=opt["text"],
                )
                for opt in localized["options"]
            ],
            data_element=localized.get("data_element"),
            phase=phase,
            progress_percent=round(progress, 1),
        )


def _localize_chief_complaint_prompt(language: str) -> str:
    prompts = {
        "en": "What is your main health problem or complaint today?",
        "hi": "आज आपकी मुख्य स्वास्थ्य समस्या या शिकायत क्या है?",
        "mr": "आज तुमची मुख्य आरोग्य समस्या किंवा तक्रार काय आहे?",
        "bn": "আজ আপনার প্রধান স্বাস্থ্য সমস্যা বা অভিযোগ কী?",
        "ta": "இன்று உங்கள் முக்கிய உடல்நலப் பிரச்சனை அல்லது புகார் என்ன?",
        "te": "ఈ రోజు మీ ప్రధాన ఆరోగ్య సమస్య లేదా ఫిర్యాదు ఏమిటి?",
    }
    return prompts.get(language, prompts["en"])


# Singleton
flow_controller = FlowController()
