import httpx
import asyncio
import time

async def run():
    url = "https://grape-alumni-hypnotize.ngrok-free.dev"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MediKiosk-Backend/1.0",
        "ngrok-skip-browser-warning": "true",
    }
    
    payload = {
        "system_prompt": "You are a helpful assistant.",
        "user_prompt": "Say hello in one word.",
        "temperature": 0.1,
        "max_tokens": 10
    }
    
    print("Testing minimal inference request...")
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(f"{url}/api/v1/clinical-infer", json=payload, headers=headers)
            elapsed = time.time() - t0
            print(f"Status: {res.status_code} in {elapsed:.2f}s")
            print("Response:", res.text)
    except Exception as e:
        print(f"Exception type: {type(e).__name__}, details: {e}")

if __name__ == "__main__":
    asyncio.run(run())
