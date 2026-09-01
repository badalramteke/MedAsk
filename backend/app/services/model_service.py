import re
import logging
from typing import Dict, Any, List, Optional
from app.models.ai import (
    ModelCapability,
    ModelTaskRequest,
    ModelTaskResponse,
    StructuredNarrationResult,
    MedicalImageFindings,
    ClinicalSummaryDraft,
)
from app.services.prompt_templates import (
    NARRATION_STRUCTURING_SYSTEM_V1,
    IMAGE_ANALYSIS_SYSTEM_V1,
    SUMMARY_SYNTHESIS_SYSTEM_V1,
)
from app.services.adapters.base import BaseModelAdapter
from app.services.adapters.medgemma import ColabMedGemmaAdapter
from app.services.adapters.gemini import GeminiAdapter
from app.services.adapters.mock import MockModelAdapter

logger = logging.getLogger("model_service")

# Prohibited clinical terms for non-diagnostic safety gating (PRD Section 11.4)
PROHIBITED_DIAGNOSTIC_PATTERNS = [
    r"you have (been diagnosed with|a severe case of|contracted)",
    r"i diagnose you with",
    r"my diagnosis is",
    r"you must take (this medication|these pills|antibiotics)",
    r"prescribe \w+ to the patient",
    r"definitely suffering from",
]


class ModelService:
    """
    Centralized AI Model Service Orchestrator.
    - Capability-based routing
    - Cascading fallback (Colab MedGemma -> Gemini -> Mock)
    - Output schema validation
    - Non-diagnostic clinical safety gating
    - Safe degradation handling
    """
    def __init__(self):
        self.primary_adapter = ColabMedGemmaAdapter()
        self.fallback_adapter = GeminiAdapter()
        self.mock_adapter = MockModelAdapter()
        self.adapters: List[BaseModelAdapter] = [
            self.primary_adapter,
            self.fallback_adapter,
            self.mock_adapter,
        ]

    async def get_health_status(self) -> Dict[str, Any]:
        """Check availability across all configured adapters."""
        status = {}
        for adapter in self.adapters:
            status[adapter.name] = await adapter.health_check()
        return status

    async def structure_narration(self, narration_text: str, language: str = "en", session_id: Optional[str] = None) -> ModelTaskResponse:
        """Parse raw patient free-text narration into structured clinical entities."""
        request = ModelTaskRequest(
            capability=ModelCapability.TEXT_NARRATION_STRUCTURING,
            task_name="structure_narration",
            language=language,
            untrusted_input=narration_text,
            session_id=session_id,
        )
        return await self._execute_cascade(request, NARRATION_STRUCTURING_SYSTEM_V1)

    async def analyze_medical_image(self, image_base64: str, modality_hint: str = "CHEST_XRAY", session_id: Optional[str] = None) -> ModelTaskResponse:
        """Analyze medical imaging (X-rays, sonography, CT) for candidate visual observations."""
        request = ModelTaskRequest(
            capability=ModelCapability.MEDICAL_IMAGE_ANALYSIS,
            task_name="analyze_medical_image",
            untrusted_input=f"Analyze this {modality_hint} medical image.",
            image_base64=image_base64,
            session_id=session_id,
        )
        return await self._execute_cascade(request, IMAGE_ANALYSIS_SYSTEM_V1, is_multimodal=True)

    async def synthesize_clinical_summary(
        self,
        interview_facts: Dict[str, Any],
        ocr_extracted_documents: List[Dict[str, Any]],
        session_id: Optional[str] = None,
    ) -> ModelTaskResponse:
        """
        Module C: Ingests structured interview facts + source-tagged OCR records
        and synthesizes a physician-ready clinical draft summary with explicit source citations.
        """
        combined_payload = {
            "patient_interview_history": interview_facts,
            "source_tagged_ocr_documents": ocr_extracted_documents,
        }
        import json
        request = ModelTaskRequest(
            capability=ModelCapability.SUMMARY_SYNTHESIS,
            task_name="synthesize_clinical_summary",
            untrusted_input=json.dumps(combined_payload, indent=2),
            document_sources=ocr_extracted_documents,
            session_id=session_id,
        )
        return await self._execute_cascade(request, SUMMARY_SYNTHESIS_SYSTEM_V1)

    async def _execute_cascade(
        self, request: ModelTaskRequest, system_prompt: str, is_multimodal: bool = False
    ) -> ModelTaskResponse:
        """Execute request across adapters in priority order with safety validation."""
        for adapter in self.adapters:
            try:
                if is_multimodal:
                    response = await adapter.generate_multimodal(request, system_prompt)
                else:
                    response = await adapter.generate_structured(request, system_prompt)

                if response.success and response.structured_payload:
                    # Run Safety Gate Filter
                    is_safe, violation = self._validate_safety(response)
                    if is_safe:
                        response.safety_validation_passed = True
                        return response
                    else:
                        logger.warning(f"Safety violation on {adapter.name}: {violation}")
                        continue
            except Exception as e:
                logger.error(f"Error calling {adapter.name}: {e}")
                continue

        # If everything fails, return deterministic mock as safe degradation
        logger.info("Falling back to MockModelAdapter for graceful degradation.")
        if is_multimodal:
            return await self.mock_adapter.generate_multimodal(request, system_prompt)
        return await self.mock_adapter.generate_structured(request, system_prompt)

    def _validate_safety(self, response: ModelTaskResponse) -> tuple[bool, str]:
        """Ensure no autonomous diagnoses or treatment prescriptions were generated."""
        text_to_check = (response.raw_response or "") + str(response.structured_payload or "")
        text_lower = text_to_check.lower()

        for pattern in PROHIBITED_DIAGNOSTIC_PATTERNS:
            if re.search(pattern, text_lower):
                return False, f"Prohibited clinical assertion matching pattern: '{pattern}'"

        return True, ""


# Singleton instance
model_service = ModelService()
