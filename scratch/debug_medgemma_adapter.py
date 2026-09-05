import os
import sys
import json
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

from app.services.adapters.medgemma import ColabMedGemmaAdapter
from app.services.prompt_templates import SUMMARY_SYNTHESIS_SYSTEM_V1
from app.models.ai import ModelTaskRequest, ModelCapability, ClinicalSummaryDraft

async def main():
    adapter = ColabMedGemmaAdapter()
    
    request = ModelTaskRequest(
        capability=ModelCapability.SUMMARY_SYNTHESIS,
        task_name="synthesize_clinical_summary",
        language="en",
        untrusted_input=json.dumps({
            "patient_interview_history": {
                "answered_questions": {
                    "__CHIEF_COMPLAINT__": "Crushing chest pain for 2 hours",
                    "past_medical_history": "T2DM, HTN",
                    "medications": "Metformin 500mg"
                }
            },
            "source_tagged_ocr_documents": [],
            "requested_patient_language": "en"
        })
    )

    print("Calling generate_structured on ColabMedGemmaAdapter...")
    res = await adapter.generate_structured(request, SUMMARY_SYNTHESIS_SYSTEM_V1)
    print("Success:", res.success)
    print("Error:", res.error_message)
    print("Structured Payload keys:", list(res.structured_payload.keys()) if isinstance(res.structured_payload, dict) else res.structured_payload)
    
    if res.structured_payload:
        try:
            draft = ClinicalSummaryDraft(**res.structured_payload)
            print("[SUCCESS] ClinicalSummaryDraft instantiated cleanly!")
        except Exception as e:
            print("[FAIL] Pydantic validation error:", e)

if __name__ == "__main__":
    asyncio.run(main())
