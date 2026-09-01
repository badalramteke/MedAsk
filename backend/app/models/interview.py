from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class InterviewState(BaseModel):
    """
    Tracks where the patient currently is in the interview flow.
    Stored as part of the session, updated after every answer.
    """
    current_phase: Literal[
        "CHIEF_COMPLAINT",
        "SOCRATES_DEEP_DIVE",
        "GENERAL_HISTORY",
        "REVIEW_OF_SYSTEMS",
        "INTERVIEW_COMPLETE"
    ] = Field(default="CHIEF_COMPLAINT")
    current_question_id: Optional[str] = Field(None, description="The ID of the next question to present.")
    active_symptom_domain: Optional[str] = Field(None, description="If in SOCRATES, which domain (e.g., chest_pain, headache).")
    answered_question_ids: List[str] = Field(default_factory=list, description="All question IDs already answered.")
    answer_history: Dict[str, Any] = Field(default_factory=dict, description="Map of question_id -> submitted value_code(s).")
    is_complete: bool = Field(default=False)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class QuestionOption(BaseModel):
    """A single selectable option for a question."""
    option_id: str
    value_code: str
    text: str  # Already localized to patient's preferred_language


class QuestionResponse(BaseModel):
    """Payload sent to the frontend — the next question to show the patient."""
    question_id: str
    question_text: str  # Localized
    input_type: Literal["single_select", "multi_select", "free_text", "numeric"]
    options: List[QuestionOption] = Field(default_factory=list)
    data_element: Optional[str] = Field(None, description="PDO path this answer maps to (e.g., hpi.chest_pain.site)")
    phase: str  # Current interview phase
    progress_percent: Optional[float] = None
    # Special answer states always available
    allows_unknown: bool = Field(default=True)
    allows_refused: bool = Field(default=True)


class AnswerSubmission(BaseModel):
    """Payload received from the frontend — the patient's answer."""
    question_id: str = Field(..., examples=["__CHIEF_COMPLAINT__"])
    selected_value_codes: List[str] = Field(default_factory=list, description="For single/multi select questions.", examples=[["RADIATION_LEFT_ARM_SHOULDER"]])
    free_text: Optional[str] = Field(None, description="For free_text or clarification input.", examples=["chest pain"])
    answer_state: Literal["ANSWERED", "UNKNOWN", "REFUSED"] = Field(default="ANSWERED")


class RedFlagAlert(BaseModel):
    """A triggered red-flag alert for triage staff."""
    rule_id: str
    category: str
    urgency_level: Literal["EMERGENCY_CRITICAL", "URGENT_PRIORITY"]
    alert_message: str  # Localized
    action_code: str
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    evidence_summary: Optional[str] = None
    acknowledged: bool = Field(default=False)


class AnswerResult(BaseModel):
    """Response after submitting an answer — tells frontend what happened."""
    success: bool
    next_question: Optional[QuestionResponse] = None
    new_alerts: List[RedFlagAlert] = Field(default_factory=list)
    interview_complete: bool = Field(default=False)
