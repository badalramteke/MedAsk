import os
import sys
import json
import asyncio
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

from app.services.adapters.medgemma import ColabMedGemmaAdapter
from app.services.prompt_templates import SUMMARY_SYNTHESIS_SYSTEM_V1
from app.models.ai import ModelTaskRequest, ModelCapability

async def main():
    adapter = ColabMedGemmaAdapter()
    print("Connecting to:", adapter.base_url)
    
    request = ModelTaskRequest(
        capability=ModelCapability.SUMMARY_SYNTHESIS,
        task_name="synthesize_clinical_summary",
        language="en",
        untrusted_input=json.dumps({
            "patient_interview_history": {
                "answered_questions": {
                    "__CHIEF_COMPLAINT__": "Severe crushing chest pain radiating to left arm for 2 hours",
                    "socrates_site": "retrosternal",
                    "socrates_character": "crushing"
                }
            },
            "source_tagged_ocr_documents": [
                {
                    "document_id": "DOC_001",
                    "type": "DISCHARGE_SUMMARY",
                    "extracted_text": "History of T2DM on Metformin 500mg.",
                    "source_tag": "[Doc#1: Discharge Summary]"
                }
            ],
            "requested_patient_language": "en"
        }, indent=2)
    )

    print("\nSending request to MedGemma...")
    response = await adapter.generate_structured(request, SUMMARY_SYNTHESIS_SYSTEM_V1)
    
    print("\n--- MedGemma Direct Adapter Response ---")
    print("Success:", response.success)
    print("Provider:", response.provider_used)
    print("Model:", response.model_name)
    print("Latency:", response.latency_ms, "ms")
    print("Error:", response.error_message)
    print("Raw Response:\n", response.raw_response)
    print("Structured Payload:\n", json.dumps(response.structured_payload, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
