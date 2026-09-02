import httpx
import asyncio

async def check():
    url = "https://grape-alumni-hypnotize.ngrok-free.dev/health"
    headers = {
        "User-Agent": "MediKiosk-Backend/1.0",
        "ngrok-skip-browser-warning": "true",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, headers=headers)
        print("Status code:", r.status_code)
        print("Headers:", r.headers)
        print("Body preview:", r.text[:300])

if __name__ == "__main__":
    asyncio.run(check())
