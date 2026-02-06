from fastapi import APIRouter, UploadFile, File
from datetime import datetime
import uuid
import shutil

from app.services.speech_to_text import transcribe_call
from app.services.transcript_parser import parse_gemini_transcript
from app.services.transcript_store import save_transcript
from app.models.transcript import Transcript

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/transcribe")
async def transcribe_agent_call(
    agent_id: str,
    file: UploadFile = File(...)
):
    temp_path = f"temp/{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1️⃣ Transcribe
    raw_text = transcribe_call(temp_path)

    # 2️⃣ Parse
    utterances = parse_gemini_transcript(raw_text)

    # 3️⃣ Build transcript object
    transcript = Transcript(
        conversation_id=f"conv_{uuid.uuid4().hex[:12]}",
        agent_id=agent_id,
        timestamp=datetime.utcnow().isoformat(),
        language="de",
        model="gemini-3-flash-preview",
        utterances=utterances
    )

    # 4️⃣ Persist
    save_transcript(transcript)

    return {
        "message": "Transcript saved successfully",
        "conversation_id": transcript.conversation_id
    }
