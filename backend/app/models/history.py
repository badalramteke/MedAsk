from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from .provenance import Provenance

class SocratesAssessment(BaseModel):
    """
    Structured SOCRATES symptom assessment.
    Values should map to `questions_socrates.json` value_codes where possible.
    """
    site: Optional[str] = Field(None, description="Location of symptom (e.g., CHEST_LEFT_SUBSTERNAL)")
    onset: Optional[str] = Field(None, description="How it started (e.g., SUDDEN_ACUTE)")
    character: Optional[str] = Field(None, description="Type of pain/symptom (e.g., CRUSHING_HEAVY_PRESSURE)")
    radiation: Optional[str] = Field(None, description="Does it move anywhere?")
    associated_symptoms: List[str] = Field(default_factory=list, description="Other symptoms occurring together.")
    time_course: Optional[str] = Field(None, description="Pattern over time (e.g., constant, intermittent)")
    exacerbating_relieving_factors: Optional[str] = Field(None, description="What makes it better or worse")
    severity: Optional[str] = Field(None, description="Severity rating or description")

class SymptomEntry(BaseModel):
    symptom_name: str = Field(..., description="Standardized symptom name")
    socrates: Optional[SocratesAssessment] = None
    provenance: Provenance

class PatientHistory(BaseModel):
    """
    Patient-reported and structured medical history.
    """
    chief_complaint: str = Field(..., description="Main reason for visit (free text or standardized)")
    history_of_present_illness: List[SymptomEntry] = Field(default_factory=list, description="Structured HPI")
    past_medical_history: List[str] = Field(default_factory=list)
    past_surgical_history: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)
    social_history: List[str] = Field(default_factory=list)
    menstrual_reproductive_history: Optional[Dict[str, str]] = Field(default=None, description="Menstrual & reproductive history for female patients (LMP, cycle regularity, pregnancy details)")
    review_of_systems: Dict[str, bool] = Field(default_factory=dict, description="Key: system/symptom, Value: presence (True/False)")
