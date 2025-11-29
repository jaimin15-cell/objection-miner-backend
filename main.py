# --- 1. IMPORT OUR "SHOPPING LIST" OF TOOLS ---
import os
import shutil
import uuid
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
import httpx
import aiofiles

# --- 2. "PREP WORK": LOAD KEYS & INITIALIZE APPS ---
print("Starting server...")
load_dotenv()  # Load all variables from our .env file
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not DEEPGRAM_API_KEY:
    print("FATAL ERROR: DEEPGRAM_API_KEY not found in .env file.")
    raise RuntimeError("DEEPGRAM_API_KEY is missing from .env file.")

if not GEMINI_API_KEY:
    print("FATAL ERROR: GEMINI_API_KEY not found in .env file.")
    print("WARNING: You need to add GEMINI_API_KEY to your .env file for analysis to work.")

# Initialize Gemini "Sous-Chef"
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Using gemini-flash-latest as it is the correct model name for the API
    model = genai.GenerativeModel('gemini-flash-latest') 

# Create our main FastAPI "Kitchen" app
app = FastAPI()

# --- 3. SET THE "SERVING WINDOW" (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ONLY allow our React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. CREATE OUR "ORDER SPIKE" (A simple V1.0 database) ---
db = {}

# --- 5. DEFINE THE "MASTER RECIPE" (The AI System Prompt) ---
SYSTEM_PROMPT = """
You are an expert sales analyst. Your job is to read a sales call transcript
and extract three key pieces of information:
1.  **Objections**: A list of all customer objections (e.g., "Price is too high", "Missing feature").
2.  **Competitors**: A list of all competitor names mentioned.
3.  **Ad Headline**: Based on the #1 objection, write ONE new, short, powerful ad headline for the marketing team.

Return your response ONLY in this exact JSON format, with no markdown formatting or backticks:
{
  "objections": ["objection 1", "objection 2"],
  "competitors": ["competitor 1", "competitor 2"],
  "adCopy": [
    { "headline": "The new ad headline you wrote" }
  ]
}
"""

# --- 6. CREATE THE "ORDER" DOOR (The /upload Endpoint) ---
@app.post("/upload")
async def handle_upload(audioFile: UploadFile = File(...)):
    print(f"\n--- New Order Received: {audioFile.filename} ---")
    temp_file_path = f"temp_{uuid.uuid4()}"
    
    try:
        # 1. Save to temp file (Async)
        async with aiofiles.open(temp_file_path, "wb") as buffer:
            while content := await audioFile.read(1024 * 1024): # Read in 1MB chunks
                await buffer.write(content)
        print(f"File saved to temp location: {temp_file_path}")

        # 2. Transcribe (Our "Ears"): Send the audio to Deepgram
        print("Sending to Deepgram for transcription...")
        transcript = ""
        DEEPGRAM_URL = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": audioFile.content_type
        }

        # Stream the file to Deepgram
        async def file_generator():
            async with aiofiles.open(temp_file_path, "rb") as f:
                while chunk := await f.read(1024 * 1024):
                    yield chunk

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(DEEPGRAM_URL, headers=headers, content=file_generator())

        if response.status_code == 200:
            response_json = response.json()
            transcript = response_json.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "No speech detected.")
        else:
            error_text = response.text
            raise HTTPException(status_code=500, detail=f"Deepgram API Error: {error_text}")

        print("Transcript received from Deepgram.")

        # 3. Analyze (Our "Brain"): Send the transcript to Gemini
        print("Sending transcript to Gemini for analysis...")
        if not GEMINI_API_KEY:
             raise HTTPException(status_code=500, detail="GEMINI_API_KEY is missing. Please check your .env file.")

        analysis_json = {}
        try:
            # Combine system prompt and transcript for Gemini
            full_prompt = f"{SYSTEM_PROMPT}\n\nTRANSCRIPT:\n{transcript}"
            
            print("DEBUG: Calling Gemini generate_content_async...")
            response = await model.generate_content_async(full_prompt)
            analysis_text = response.text
            print(f"DEBUG: Gemini Response: {analysis_text}")
            
            # Clean up potential markdown formatting from Gemini
            analysis_text = analysis_text.replace("```json", "").replace("```", "").strip()
            
            analysis_json = json.loads(analysis_text)
            print(f"DEBUG: analysis_json parsed successfully: {analysis_json.keys()}")

        except Exception as e:
            print(f"Gemini API Error: {e}")
            raise HTTPException(status_code=502, detail=f"Gemini Error: {str(e)}")

        print("Analysis received from Gemini.")

        final_report = {
            "transcript": transcript,
            **analysis_json
        }

        report_id = str(uuid.uuid4())[:8]
        db[report_id] = final_report
        print(f"Report {report_id} created and stored in memory.")

        return {"reportId": report_id}

    except Exception as e:
        print(f"---!!! ERROR processing file {audioFile.filename}: {e} ---")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    finally:
        # 4. Cleanup: Always remove the temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temp file: {temp_file_path}")

# --- 7. CREATE THE "PICKUP WINDOW" (The /report/{id} Endpoint) ---
@app.get("/report/{id}")
async def get_report(id: str):
    print(f"\n--- Frontend requesting report {id} ---")
    report = db.get(id)
    if not report:
        print(f"Report {id} NOT FOUND in memory-db.")
        raise HTTPException(status_code=404, detail="Report not found or is still processing.")
    print(f"Report {id} found. Sending to frontend.")
    return report

# --- 8. (For development) A simple "Home" route for the backend ---
@app.get("/")
async def root():
    return {"message":"ObjectionMiner AI Backend is running (powered by Gemini)!"}
# --- END OF FILE ---