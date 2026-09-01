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
        r = await client.get(f"{url}/openapi.json", headers=headers)
        spec = r.json()
        print("Components schemas:")
        print(json.dumps(spec.get("components", {}).get("schemas", {}), indent=2))

if __name__ == "__main__":
    asyncio.run(inspect())
