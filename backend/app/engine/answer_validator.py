"""
AnswerValidator: Validates submitted answers against JSON dataset options
and applies valid answers to the PatientDataObject.
"""
from typing import List, Optional
from app.engine.question_bank import question_bank


class AnswerValidator:
    def validate_answer(
        self, question_id: str, selected_value_codes: List[str], free_text: Optional[str]
    ) -> tuple[bool, str]:
        """
        Validate that the submitted answer is valid for the given question.
        Returns (is_valid, error_message).
        """
        question = question_bank.get_question(question_id)
        if not question:
            # Chief complaint is a special synthetic question
            if question_id == "__CHIEF_COMPLAINT__":
                if free_text and len(free_text.strip()) > 0:
                    return True, ""
                return False, "Chief complaint cannot be empty."
            return False, f"Unknown question_id: {question_id}"

        input_type = question.get("input_type", "single_select")

        if input_type == "free_text":
            if not free_text or len(free_text.strip()) == 0:
                return False, "Free text answer cannot be empty."
            return True, ""

        # For select questions, validate value_codes against allowed options
        allowed_codes = {opt["value_code"] for opt in question.get("options", [])}

        if not selected_value_codes:
            return False, "No option selected."

        if input_type == "single_select" and len(selected_value_codes) > 1:
            return False, "Only one option can be selected for single_select questions."

        invalid_codes = [code for code in selected_value_codes if code not in allowed_codes]
        if invalid_codes:
            return False, f"Invalid value code(s): {invalid_codes}. Allowed: {sorted(allowed_codes)}"

        return True, ""


# Singleton
answer_validator = AnswerValidator()
