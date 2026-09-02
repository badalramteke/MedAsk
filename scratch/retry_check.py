import httpx
import asyncio

async def retry_check():
    url = "https://grape-alumni-hypnotize.ngrok-free.dev/health"
    headers = {
        "User-Agent": "MediKiosk-Backend/1.0",
        "ngrok-skip-browser-warning": "true",
    }
    for i in range(3):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(url, headers=headers)
                print(f"Attempt {i+1}: {r.status_code} - {r.text[:100]}")
                return
        except Exception as e:
            print(f"Attempt {i+1}: {type(e).__name__} - {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(retry_check())
