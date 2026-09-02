import os
import sys
import json
import asyncio
from pprint import pprint
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

from app.services.adapters.medgemma import ColabMedGemmaAdapter
from app.services.model_service import model_service
from app.models.ai import ClinicalSummaryDraft

async def main():
    print("=== Testing MedGemma Summary Generation ===")
    adapter = ColabMedGemmaAdapter()
    health = await adapter.health_check()
    print("MedGemma Health Check:", health)
    
    if health.get("status") != "online":
        print("[!] MedGemma health check failed or server is offline. Details:", health)
        return

    # Realistic patient interview history
    interview_facts = {
        "answered_questions": {
            "__CHIEF_COMPLAINT__": "Severe crushing chest pain radiating to left arm for 2 hours, with cold sweating and mild breathlessness",
            "socrates_site": ["chest_retrosternal", "left_shoulder_radiation"],
            "socrates_onset": "Sudden onset while walking upstairs",
            "socrates_character": ["crushing", "heavy_pressure"],
            "socrates_radiation": "Radiates down the left medial arm to fingers",
            "socrates_associated": ["diaphoresis", "dyspnea_mild", "nausea_no_vomiting"],
            "socrates_timing": "Constant pain for the past 2 hours without relief",
            "socrates_exacerbating": ["walking", "deep_breathing"],
            "socrates_severity": "8/10",
            "past_medical_history": ["Type 2 Diabetes Mellitus x 5 yrs", "Hypertension x 3 yrs"],
            "past_surgical_history": "Denies previous surgeries",
            "medications": ["Tab Metformin 500mg BD", "Tab Telmisartan 40mg OD"],
            "allergies": "No known drug allergies (NKDA)",
            "family_history": ["Father died of myocardial infarction at age 52", "Mother has hypertension"],
            "personal_social_history": ["Smoker 10 pack-years", "Occasional alcohol", "High stress office job"],
            "review_of_systems": ["Denies fever, chills, cough, hemoptysis, abdominal pain, neurological deficits"]
        },
        "active_red_flags": [
            {
                "flag_id": "RED_FLAG_CHEST_PAIN_ACUTE",
                "severity": "CRITICAL",
                "message": "Potential Acute Coronary Syndrome (ACS) - Immediate ECG and Triage Required"
            }
        ],
        "patient_demographics": {
            "gender": "MALE",
            "age": 52
        },
        "facility_type": "GENERAL"
    }

    # Realistic OCR extracted documents
    ocr_extracted_documents = [
        {
            "document_id": "DOC_001",
            "type": "DISCHARGE_SUMMARY",
            "source_date": "2023-11-15",
            "extracted_text": "AIIMS OPD: Diagnosed T2DM (HbA1c 7.9%), Essential HTN. Advised Tab Metformin 500mg 1-0-1, Tab Telmisartan 40mg 1-0-0. Diet modification advised.",
            "source_tag": "[Doc#1: AIIMS OPD Slip 2023-11-15]"
        },
        {
            "document_id": "DOC_002",
            "type": "LAB_REPORT",
            "source_date": "2024-04-10",
            "extracted_text": "Pathology Lab: Fasting Blood Sugar: 154 mg/dL (Ref: 70-100), Serum Creatinine: 1.0 mg/dL (Ref: 0.7-1.3), Total Cholesterol: 220 mg/dL (High, Ref: <200), LDL: 140 mg/dL.",
            "source_tag": "[Doc#2: Lab Report 2024-04-10]"
        }
    ]

    print("\n--- Dispatching synthesis request to ModelService (Primary: MedGemma) ---")
    response = await model_service.synthesize_clinical_summary(
        interview_facts=interview_facts,
        ocr_extracted_documents=ocr_extracted_documents,
        language="en",
        session_id="session_live_test_001"
    )

    print(f"\nResponse Received in {response.latency_ms:.1f}ms")
    print("Success:", response.success)
    print("Provider Used:", response.provider_used)
    print("Model Name:", response.model_name)
    print("Safety Validation Passed:", response.safety_validation_passed)
    
    if not response.success:
        print("Error message:", response.error_message)
        print("Raw response:", response.raw_response)
        return

    print("\n--- Structured Payload ---")
    pprint(response.structured_payload)

    print("\n--- Validating against ClinicalSummaryDraft schema ---")
    try:
        draft = ClinicalSummaryDraft(**response.structured_payload)
        print("Schema Validation: PASS!")
        print("\n=== Summary Breakdown ===")
        print("Chief Complaint:", draft.patient_chief_complaint)
        print("HPI:", draft.hpi_summary)
        print("Past Medical/Surgical:", draft.past_medical_surgical_summary)
        print("Meds & Allergies:", draft.medications_and_allergies)
        print("Family History:", draft.family_history_summary)
        print("Personal/Social History:", draft.personal_social_history_summary)
        print("ROS:", draft.review_of_systems_summary)
        print("Investigations/Labs:", draft.investigations_and_lab_summary)
        print("Clinician Review Flags:", draft.clinician_review_flags)
        print("Patient Audio Script:", draft.patient_audio_script_local_lang)
        print(f"Citations Count: {len(draft.source_citations)}")
    except Exception as e:
        print("Schema Validation FAILED:", e)

if __name__ == "__main__":
    asyncio.run(main())
