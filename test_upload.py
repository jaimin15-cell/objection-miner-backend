import httpx
import asyncio

async def main():
    url = "http://127.0.0.1:8001/upload"
    files = {'audioFile': ('test_speech.wav', open('test_speech.wav', 'rb'), 'audio/wav')}

    try:
        print(f"Sending POST request to {url}...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, timeout=60.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(main())
