from fastapi import FastAPI, UploadFile, File
import shutil
import os
import json
from datetime import datetime

from services.speech_to_text import transcribe_call
from ai.hate_detector import detect_hate_from_textfile
from ai.summarizer import summarize_hate_report
from ai.therapy_bot import agent_therapy_chat
from ai.manager_coach import coach_manager

app = FastAPI(title="Agent Support Platform")

# ---------------------------
# Directory setup (ONCE)
# ---------------------------
BASE_DATA_DIR = "data"
AGENT_ID = "agent_12"

TRANSCRIPTS_DIR = f"{BASE_DATA_DIR}/transcripts/{AGENT_ID}"
DETECTIONS_DIR = f"{BASE_DATA_DIR}/detections/{AGENT_ID}"
SUMMARIES_DIR = f"{BASE_DATA_DIR}/summaries/{AGENT_ID}"
TEMP_DIR = "temp"

for directory in [
    TRANSCRIPTS_DIR,
    DETECTIONS_DIR,
    SUMMARIES_DIR,
    TEMP_DIR
]:
    os.makedirs(directory, exist_ok=True)

# ---------------------------
# 1️⃣ Audio Transcription + Hate Detection
# ---------------------------
@app.post("/agent/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    temp_audio_path = f"{TEMP_DIR}/{file.filename}"
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcribe
    transcript_text = transcribe_call(temp_audio_path)

    # Save transcript
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    conversation_id = f"conv_{timestamp}"
    transcript_path = f"{TRANSCRIPTS_DIR}/{conversation_id}.txt"
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    # Hate detection
    detection_report = detect_hate_from_textfile(transcript_path)
    detection_path = f"{DETECTIONS_DIR}/{conversation_id}.json"
    with open(detection_path, "w", encoding="utf-8") as f:
        json.dump(detection_report, f, indent=2, ensure_ascii=False)

    # Summary
    summary = summarize_hate_report(detection_report)
    summary_path = f"{SUMMARIES_DIR}/{conversation_id}_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return {
        "conversation_id": conversation_id,
        "incident_count": detection_report["incident_count"],
        "overall_severity": detection_report["overall_severity"],
        "summary": summary
    }

# ---------------------------
# 2️⃣ Agent Therapy Chatbot
# ---------------------------
@app.post("/agent/chat")
async def chat_agent(message: str):
    return agent_therapy_chat(agent_id=AGENT_ID, agent_message=message)

# ---------------------------
# 3️⃣ Manager Coach Chatbot
# ---------------------------
@app.post("/manager/chat")
async def chat_manager(question: str):
    return coach_manager(agent_id=AGENT_ID, manager_question=question)

# ---------------------------
# 4️⃣ Optional: Fetch Summaries
# ---------------------------
@app.get("/manager/summaries")
async def get_summaries(limit: int = 5):
    files = sorted(
        [f for f in os.listdir(SUMMARIES_DIR) if f.endswith("_summary.json")],
        reverse=True
    )
    summaries = []
    for file in files[:limit]:
        with open(os.path.join(SUMMARIES_DIR, file), "r", encoding="utf-8") as f:
            summaries.append(json.load(f))
    return {"agent_id": AGENT_ID, "summaries": summaries}
