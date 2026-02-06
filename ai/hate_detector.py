import re
from typing import Dict

# Hate keywords with severity
HATE_KEYWORDS = {
    "mistkerl": 0.7,
    "idiot": 0.5,
    "stupid": 0.4,
    "bitch": 0.6,
    "nigga": 0.9,
    "useless": 0.5
}

def detect_hate_from_textfile(file_path: str) -> Dict:
    """
    Reads a transcript text file and returns detected hate events.
    Handles Gemini-style transcripts, parentheses in speaker labels, and punctuation.
    """
    hate_events = []

    conversation_id = file_path.split("/")[-1].replace(".txt", "")
    agent_id = file_path.split("/")[-2]

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Flexible regex: handles parentheses after speaker
        match = re.match(r"\[(\d{2}:\d{2})\]\s*(Speaker\s*\d+)(?:\s*\(.*?\))?:\s*(.+)", line)
        if not match:
            continue

        time, speaker, text = match.groups()

        # Only scan Speaker 2 (customer) — change to '1' if needed
        if "2" not in speaker:
            continue

        # Remove any remaining parentheses prefix
        text = re.sub(r'^\(.*?\):\s*', '', text)

        # Lowercase and strip punctuation for matching
        text_lower = text.lower().replace(".", "").replace(",", "").replace("!", "").replace("?", "")

        for kw, severity in HATE_KEYWORDS.items():
            if kw in text_lower:
                hate_events.append({
                    "timestamp": time,
                    "speaker": "customer",
                    "text": text,
                    "category": "insult",
                    "severity": severity
                })

    overall_severity = max([e["severity"] for e in hate_events], default=0)

    return {
        "conversation_id": conversation_id,
        "agent_id": agent_id,
        "hate_events": hate_events,
        "overall_severity": overall_severity,
        "incident_count": len(hate_events)
    }
