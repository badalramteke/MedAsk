import httpx
import asyncio
import json

async def inspect():
    url = "https://grape-alumni-hypnotize.ngrok-free.dev"
    headers = {
        "User-Agent": "MediKiosk-Backend/1.0",
        "ngrok-skip-browser-warning": "true",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Check openapi.json
        try:
            r = await client.get(f"{url}/openapi.json", headers=headers)
            print("OpenAPI status:", r.status_code)
            if r.status_code == 200:
                spec = r.json()
                print("Paths available:", list(spec.get("paths", {}).keys()))
                print("\nFull schemas:")
                print(json.dumps(spec.get("paths", {}), indent=2))
        except Exception as e:
            print("OpenAPI error:", e)

if __name__ == "__main__":
    asyncio.run(inspect())
