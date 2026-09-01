import time
from typing import Dict, Any
from app.services.adapters.base import BaseModelAdapter
from app.models.ai import ModelTaskRequest, ModelTaskResponse, ModelCapability


class MockModelAdapter(BaseModelAdapter):
    """
    Deterministic Offline Mock Adapter for testing and fallback when GPU/Network is unavailable.
    """
    def __init__(self):
        super().__init__(name="mock")

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "online", "code": 200, "details": "Mock provider ready"}

    async def generate_structured(self, request: ModelTaskRequest, system_prompt: str) -> ModelTaskResponse:
        start_time = time.time()
        
        if request.capability == ModelCapability.TEXT_NARRATION_STRUCTURING:
            payload = {
                "primary_symptom": "chest_pain",
                "site": "substernal",
                "onset": "acute (2 hours ago)",
                "character": "crushing pressure",
                "radiation": "left arm and jaw",
                "severity": "8/10",
                "associated_symptoms": ["dyspnea", "diaphoresis"],
                "uncertainty_notes": None
            }
        elif request.capability == ModelCapability.SUMMARY_SYNTHESIS:
            payload = {
                "patient_chief_complaint": "Acute retrosternal chest pain with left arm radiation [Patient-Reported]",
                "hpi_summary": "Patient presented with 2 hours of sudden-onset crushing chest pain radiating to left shoulder and arm [Patient-Reported].",
                "past_medical_surgical_summary": "Type 2 Diabetes Mellitus x 5 years, Hypertension [Doc#1: Discharge Summary 2024-05-10]. No prior surgeries [Patient-Reported].",
                "medications_and_allergies": "Metformin 500mg BD, Telmisartan 40mg OD [Doc#2: Prescription Dr. Sharma]. No known drug allergies [Patient-Reported].",
                "family_history_summary": "Father had myocardial infarction at age 55 [Patient-Reported]. Mother is diabetic [Patient-Reported].",
                "personal_social_history_summary": "Non-smoker, occasional alcohol use. Sedentary occupation (desk job). Vegetarian diet [Patient-Reported].",
                "review_of_systems_summary": "Cardiovascular: chest pain as described. Respiratory: denies cough, dyspnea at rest. GI: denies nausea, vomiting. Neurological: denies dizziness, syncope [Patient-Reported].",
                "investigations_and_lab_summary": "Fasting Blood Sugar: 142 mg/dL (High) [Doc#3: Lab Report 2024-05-12], HbA1c: 7.8% (Borderline High) [Doc#3].",
                "imaging_findings_summary": "Chest X-Ray PA View: Normal cardiothoracic ratio, no active consolidation [Doc#4: Imaging 2024-05-15].",
                "menstrual_reproductive_summary": None,
                "ayush_summary": None,
                "clinician_review_flags": [],
                "source_citations": [
                    {"finding_text": "Retrosternal chest pain", "source_tag": "[Patient-Reported]", "category": "HISTORY"},
                    {"finding_text": "T2DM & Hypertension", "source_tag": "[Doc#1: Discharge Summary 2024-05-10]", "category": "HISTORY"},
                    {"finding_text": "Metformin 500mg BD, Telmisartan 40mg", "source_tag": "[Doc#2: Prescription Dr. Sharma]", "category": "MEDICATION"},
                    {"finding_text": "FBS: 142 mg/dL, HbA1c: 7.8%", "source_tag": "[Doc#3: Lab Report 2024-05-12]", "category": "LAB_INVESTIGATION"}
                ],
                "patient_audio_script_local_lang": "Mock Audio: You reported chest pain for 2 hours. We have noted your medical history of diabetes and hypertension.",
                "is_draft_for_clinician_review": True
            }
        else:
            payload = {"status": "success", "note": "generic mock structured output"}

        latency = round((time.time() - start_time) * 1000, 2)
        return ModelTaskResponse(
            success=True,
            capability=request.capability,
            provider_used=self.name,
            model_name="mock-deterministic-v1",
            prompt_version=request.prompt_version,
            latency_ms=latency,
            confidence_score=1.0,
            structured_payload=payload,
        )

    async def generate_multimodal(self, request: ModelTaskRequest, system_prompt: str) -> ModelTaskResponse:
        start_time = time.time()
        payload = {
            "modality": "CHEST_XRAY",
            "anatomical_region": "Thorax / Lungs",
            "candidate_observations": [
                "Clear bilateral lung fields without focal consolidation",
                "Normal cardiothoracic ratio (< 0.5)",
                "Clear costophrenic angles bilaterally"
            ],
            "uncertainty_level": "LOW",
            "requires_radiologist_review": True
        }
        latency = round((time.time() - start_time) * 1000, 2)
        return ModelTaskResponse(
            success=True,
            capability=request.capability,
            provider_used=self.name,
            model_name="mock-multimodal-v1",
            prompt_version=request.prompt_version,
            latency_ms=latency,
            confidence_score=1.0,
            structured_payload=payload,
        )
