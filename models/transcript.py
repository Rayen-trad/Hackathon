from typing import List
from pydantic import BaseModel

class Utterance(BaseModel):
    time: str
    speaker: str   # "agent" | "customer"
    text: str

class Transcript(BaseModel):
    conversation_id: str
    agent_id: str
    timestamp: str
    language: str
    model: str
    utterances: List[Utterance]
