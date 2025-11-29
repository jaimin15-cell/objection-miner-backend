import os
from dotenv import load_dotenv

load_dotenv()

deepgram_key = os.getenv("DEEPGRAM_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

print(f"Deepgram Key present: {bool(deepgram_key)}")
if deepgram_key:
    print(f"Deepgram Key length: {len(deepgram_key)}")
    print(f"Deepgram Key start: {deepgram_key[:4]}...")

print(f"OpenAI Key present: {bool(openai_key)}")
if openai_key:
    print(f"OpenAI Key start: {openai_key[:3]}...")
