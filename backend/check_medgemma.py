import os
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

MEDGEMMA_URL = os.getenv("COLAB_MEDGEMMA_URL")

async def check_medgemma():
    if not MEDGEMMA_URL:
        print("Error: COLAB_MEDGEMMA_URL is not set in the .env file.")
        return False

    print(f"Checking MedGemma connection at: {MEDGEMMA_URL}")
    
    # We will try a simple health check or models endpoint typically provided by vLLM/FastAPI
    test_endpoint = f"{MEDGEMMA_URL.rstrip('/')}/health"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(test_endpoint)
            if response.status_code == 200:
                print("✅ Successfully connected to MedGemma provider.")
                return True
            else:
                print(f"⚠️ Connected, but received unexpected status code: {response.status_code}")
                return False
    except httpx.RequestError as e:
        print(f"❌ Connection failed. Ensure the Colab ngrok tunnel is active and the URL is correct in .env.")
        print(f"Details: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(check_medgemma())
