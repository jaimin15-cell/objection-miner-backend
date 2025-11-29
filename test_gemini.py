import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_try = [
    'gemini-1.5-flash',
    'models/gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'models/gemini-1.5-flash-latest',
    'gemini-pro',
    'models/gemini-pro'
]

for model_name in models_to_try:
    print(f"Trying model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, are you working?")
        print(f"SUCCESS with {model_name}: {response.text}")
        break
    except Exception as e:
        print(f"FAILED with {model_name}: {e}")
