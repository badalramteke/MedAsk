import httpx
import asyncio
import json

async def run():
    url = "https://grape-alumni-hypnotize.ngrok-free.dev"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MediKiosk-Backend/1.0",
        "ngrok-skip-browser-warning": "true",
    }
    
    from dotenv import load_dotenv
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))
    from app.services.prompt_templates import SUMMARY_SYNTHESIS_SYSTEM_V1
    
    payload = {
        "system_prompt": SUMMARY_SYNTHESIS_SYSTEM_V1,
        "user_prompt": "Patient: 52M with crushing chest pain 2h. Past T2DM, HTN. Meds: Metformin. Allergies: None. Family: Father MI. Smoker. ROS: denies cough. Labs: FBS 154 mg/dL.",
        "temperature": 0.1,
        "max_tokens": 600
    }
    
    async with httpx.AsyncClient(timeout=75.0) as client:
        res = await client.post(f"{url}/api/v1/clinical-infer", json=payload, headers=headers)
        if res.status_code == 200:
            raw = res.json().get("result", "")
            print("Raw length:", len(raw))
            print("=== RAW OUTPUT FROM MEDGEMMA ===")
            print(raw)
        else:
            print("Error:", res.status_code, res.text)

if __name__ == "__main__":
    asyncio.run(run())
