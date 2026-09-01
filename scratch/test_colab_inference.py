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
    
    payload = {
        "system_prompt": "You are a clinical AI medical scribe. Extract clinical summary into JSON.",
        "user_prompt": "Patient: 45M. Chief Complaint: severe chest pain for 2 hours. History: T2DM, HTN. Meds: Metformin 500mg. Return JSON with patient_chief_complaint, hpi_summary, medications_and_allergies.",
        "temperature": 0.1,
        "max_tokens": 512
    }
    
    print("Sending inference request to Colab MedGemma...")
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(f"{url}/api/v1/clinical-infer", json=payload, headers=headers)
            elapsed = time.time() - t0
            print(f"Status: {res.status_code} in {elapsed:.2f}s")
            if res.status_code == 200:
                data = res.json()
                print("Model:", data.get("model"))
                print("Result:\n", data.get("result"))
            else:
                print("Error:", res.text)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    asyncio.run(run())
