import httpx
import asyncio
import json
import time

async def run():
    url = "https://grape-alumni-hypnotize.ngrok-free.dev"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MediKiosk-Backend/1.0",
        "ngrok-skip-browser-warning": "true",
    }
    
    system_prompt = """You are a clinical AI medical scribe for MediKiosk.
Extract and synthesize the clinical history and document findings into a clean JSON draft summary.
Do NOT make any medical diagnosis or treatment recommendations.
Output JSON only with keys:
patient_chief_complaint, hpi_summary, past_medical_surgical_summary, medications_and_allergies, family_history_summary, personal_social_history_summary, review_of_systems_summary, investigations_and_lab_summary, patient_audio_script_local_lang, is_draft_for_clinician_review (true)."""

    user_prompt = """Patient: 52M.
Interview facts:
- Chief Complaint: Crushing retrosternal chest pain radiating to left arm for 2 hours with sweating [Patient-Reported]
- Past history: Type 2 Diabetes x 5y, Hypertension x 3y [Doc#1: AIIMS OPD 2023]
- Meds: Metformin 500mg, Telmisartan 40mg [Doc#1]
- Allergies: None [Patient-Reported]
- Family: Father MI at 52 [Patient-Reported]
- Personal: Smoker [Patient-Reported]
- ROS: Denies fever, cough [Patient-Reported]
- Labs: Fasting Blood Sugar 154 mg/dL [Doc#2: Lab Report 2024]

Generate the JSON draft summary now:"""

    payload = {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "temperature": 0.1,
        "max_tokens": 450
    }
    
    print("Testing MedGemma clinical summary synthesis with max_tokens=450...")
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(f"{url}/api/v1/clinical-infer", json=payload, headers=headers)
            elapsed = time.time() - t0
            print(f"Status: {res.status_code} in {elapsed:.2f}s")
            if res.status_code == 200:
                data = res.json()
                print("Model:", data.get("model"))
                print("\n=== MedGemma Output ===")
                print(data.get("result"))
            else:
                print("Error:", res.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(run())
