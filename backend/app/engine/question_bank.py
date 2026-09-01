"""
QuestionBank: Loads and indexes all clinical question JSON datasets at startup.
Provides fast lookup by question_id, symptom_domain, and section.
"""
import json
import os
from typing import Dict, List, Optional

# Resolve paths relative to project root
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "clinical")

class QuestionBank:
    def __init__(self, data_dir: str = _DATA_DIR):
        self._questions: Dict[str, dict] = {}  # question_id -> full question object
        self._socrates_domains: Dict[str, List[str]] = {}  # symptom_domain -> [question_ids in order]
        self._general_sections: Dict[str, List[str]] = {}  # section -> [question_ids in order]
        self._loaded = False
        self._data_dir = data_dir
        self._load()

    def _load(self):
        # Load SOCRATES questions
        socrates_path = os.path.join(self._data_dir, "questions_socrates.json")
        if os.path.exists(socrates_path):
            with open(socrates_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for q in data.get("questions", []):
                qid = q["question_id"]
                self._questions[qid] = q
                domain = q.get("symptom_domain", "unknown")
                if domain not in self._socrates_domains:
                    self._socrates_domains[domain] = []
                self._socrates_domains[domain].append(qid)

        # Load general intake questions
        general_path = os.path.join(self._data_dir, "questions_general_intake.json")
        if os.path.exists(general_path):
            with open(general_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for q in data.get("questions", []):
                qid = q["question_id"]
                self._questions[qid] = q
                section = q.get("section", "unknown")
                if section not in self._general_sections:
                    self._general_sections[section] = []
                self._general_sections[section].append(qid)

        self._loaded = True

    def get_question(self, question_id: str) -> Optional[dict]:
        return self._questions.get(question_id)

    def get_socrates_entry_question(self, symptom_domain: str) -> Optional[str]:
        """Get the first question_id for a SOCRATES symptom domain."""
        ids = self._socrates_domains.get(symptom_domain)
        return ids[0] if ids else None

    def get_general_entry_question(self) -> Optional[str]:
        """Get the first question_id for the general intake flow."""
        # Return the first question from the first section
        for section_ids in self._general_sections.values():
            if section_ids:
                return section_ids[0]
        return None

    def has_socrates_domain(self, symptom_domain: str) -> bool:
        return symptom_domain in self._socrates_domains

    def get_available_socrates_domains(self) -> List[str]:
        return list(self._socrates_domains.keys())

    def localize_question(self, question_id: str, language: str = "en") -> Optional[dict]:
        """Return a question with text localized to the given language."""
        q = self.get_question(question_id)
        if not q:
            return None

        localized = {
            "question_id": q["question_id"],
            "question_text": q["text_by_language"].get(language, q["text_by_language"].get("en", "")),
            "input_type": q.get("input_type", "single_select"),
            "data_element": q.get("data_element"),
            "options": [],
        }

        for opt in q.get("options", []):
            localized["options"].append({
                "option_id": opt["option_id"],
                "value_code": opt["value_code"],
                "text": opt["text_by_language"].get(language, opt["text_by_language"].get("en", "")),
            })

        return localized

    def get_next_question_id(self, question_id: str, selected_value_codes: List[str]) -> Optional[str]:
        """
        Given the current question and the patient's answer, determine the next question
        by evaluating followup_triggers in order.
        This is the core of dynamic branching.
        """
        q = self.get_question(question_id)
        if not q:
            return None

        for trigger in q.get("followup_triggers", []):
            condition = trigger.get("condition_type", "ALWAYS")
            next_qid = trigger.get("next_question_id")

            if condition == "ALWAYS":
                return next_qid
            elif condition == "VALUE_MATCH":
                target_codes = trigger.get("target_value_codes", [])
                if any(code in selected_value_codes for code in target_codes):
                    return next_qid

        return None


# Singleton instance
question_bank = QuestionBank()
