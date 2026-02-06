import json
from pathlib import Path
from app.models.transcript import Transcript

BASE_DIR = Path("data/transcripts")

def save_transcript(transcript: Transcript) -> Path:
    agent_dir = BASE_DIR / transcript.agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)

    file_path = agent_dir / f"{transcript.conversation_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(transcript.model_dump(), f, ensure_ascii=False, indent=2)

    return file_path
