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
Synthesize the clinical history into a valid JSON draft summary.
IMPORTANT: You MUST respond ONLY with a valid raw JSON object starting with { and ending with }. Do not write any thoughts, explanations, or text outside the JSON object.

Expected JSON Keys:
{
  "patient_chief_complaint": "string",
  "hpi_summary": "string",
  "past_medical_surgical_summary": "string or null",
  "medications_and_allergies": "string or null",
  "family_history_summary": "string or null",
  "personal_social_history_summary": "string or null",
  "review_of_systems_summary": "string or null",
  "investigations_and_lab_summary": "string or null",
  "imaging_findings_summary": null,
  "menstrual_reproductive_summary": null,
  "ayush_summary": null,
  "clinician_review_flags": [],
  "source_citations": [
    {"finding_text": "text", "source_tag": "[Patient-Reported]", "category": "HISTORY"}
  ],
  "patient_audio_script_local_lang": "string",
  "is_draft_for_clinician_review": true
}"""

    user_prompt = """Patient: 52M with crushing chest pain 2h. Past T2DM, HTN. Meds: Metformin. Allergies: None. Family: Father MI. Smoker. ROS: denies cough. Labs: FBS 154 mg/dL.
Produce the JSON summary:"""

    payload = {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "temperature": 0.1,
        "max_tokens": 750
    }
    
    print("Testing direct JSON enforcement on MedGemma...")
    t0 = time.time()
    async with httpx.AsyncClient(timeout=90.0) as client:
        res = await client.post(f"{url}/api/v1/clinical-infer", json=payload, headers=headers)
        elapsed = time.time() - t0
        print(f"Status: {res.status_code} in {elapsed:.2f}s")
        if res.status_code == 200:
            raw = res.json().get("result", "")
            print("=== RAW MEDGEMMA OUTPUT ===")
            print(raw)
            
            # Test JSON parse
            import re
            match = re.search(r"(\{.*\})", raw, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(1))
                    print("\n[SUCCESS] Successfully parsed JSON from MedGemma:")
                    print(json.dumps(parsed, indent=2))
                except Exception as e:
                    print("JSON parse error:", e)
            else:
                print("No JSON object found in output")

if __name__ == "__main__":
    asyncio.run(run())
