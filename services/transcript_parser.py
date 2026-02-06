import re
from typing import List
from app.models.transcript import Utterance

def parse_gemini_transcript(raw_text: str) -> List[Utterance]:
    pattern = r"\[(\d{2}:\d{2})\]\s*(Speaker\s*\d+):\s*(.+)"
    matches = re.findall(pattern, raw_text)

    utterances = []

    for time, speaker, text in matches:
        role = "agent" if "Speaker 1" in speaker else "customer"
        utterances.append(
            Utterance(time=time, speaker=role, text=text.strip())
        )

    return utterances
