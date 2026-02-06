from fastapi import FastAPI, UploadFile, File
import shutil, os
from services.speech_to_text import transcribe_call
from ai.hate_detector import detect_hate_from_textfile
from datetime import datetime

app = FastAPI(title="Agent Support Platform")

# Ensure directories exist
os.makedirs("data/transcripts/agent_12", exist_ok=True)
os.makedirs("temp", exist_ok=True)

@app.post("/agent/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Step 1: Save uploaded audio temporarily
    temp_audio_path = f"temp/{file.filename}"
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 2: Transcribe audio to text (Gemini)
    transcript_text = transcribe_call(temp_audio_path)

    # Step 3: Save transcript as TXT for hate detection
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    conversation_id = f"conv_{timestamp}"
    txt_path = f"data/transcripts/agent_12/{conversation_id}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    # Step 4: Run hate detector on TXT
    report = detect_hate_from_textfile(txt_path)

    # Step 5: Return report in API response
    return {
        "conversation_id": conversation_id,
        "incident_count": report["incident_count"],
        "overall_severity": report["overall_severity"],
        "hate_events": report["hate_events"]
    }
