import os
import sys
import json
import base64
import time
import httpx
import asyncio
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

from app.services.prompt_templates import IMAGE_ANALYSIS_SYSTEM_V1

async def analyze_xray(image_path: str):
    url = os.getenv("COLAB_MEDGEMMA_URL", "").rstrip("/")
    if not url:
        print("Error: COLAB_MEDGEMMA_URL not found in .env")
        return

    print(f"Target Colab Endpoint: {url}")
    print(f"Reading chest X-ray image: {image_path}")
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    print(f"Image Base64 size: {len(image_b64)} chars ({len(image_bytes)/1024:.1f} KB)")
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MediKiosk-Backend/1.0",
        "ngrok-skip-browser-warning": "true",
    }
    
    # Check health first
    print("\n[1] Checking Colab MedGemma health status...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            h_res = await client.get(f"{url}/health", headers=headers)
            print("Health response:", h_res.status_code, h_res.json())
        except Exception as e:
            print("[!] Health check failed:", e)
            return

    # Payload for multimodal infer
    system_prompt = IMAGE_ANALYSIS_SYSTEM_V1 + "\nIMPORTANT: Output JSON only conforming to schema."
    user_prompt = "Describe the findings, visual patterns, and observations in this chest X-ray image in detail."

    payload = {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "image_base64": image_b64,
        "temperature": 0.1,
        "max_tokens": 600
    }

    print("\n[2] Dispatching image to MedGemma /api/v1/multimodal-infer (NO FALLBACK)...")
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(f"{url}/api/v1/multimodal-infer", json=payload, headers=headers)
            elapsed = time.time() - t0
            print(f"\nResponse received in {elapsed:.2f}s (HTTP {res.status_code})")
            
            if res.status_code == 200:
                data = res.json()
                print("Model Used:", data.get("model"))
                print("Status:", data.get("status"))
                print("\n=== MEDGEMMA CHEST X-RAY ANALYSIS ===")
                print(data.get("result"))
            else:
                print(f"Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"Request Exception: {e}")

if __name__ == "__main__":
    img = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "medGemmaAndOCRtesting", "Chest X-Ray Image", "Viral Pneumonia", "1.jpg"))
    asyncio.run(analyze_xray(img))
