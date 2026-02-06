# backend/app/services/speech_to_text.py

import os
from dotenv import load_dotenv
import google.genai as genai

# Load environment variables from .env automatically
load_dotenv()

def _get_client():
    """Lazily initialize and return the Gemini AI client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. "
                         "Please check your .env file.")
    return genai.Client(api_key=api_key)

def transcribe_call(audio_path: str) -> str:
    """
    Takes an audio file path and returns a verbatim transcript
    using Gemini AI.
    """
    client = _get_client()

    # Upload the audio file
    uploaded_file = client.files.upload(file=audio_path)

    # Generate transcript
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            """
You are a forensic transcription system designed for safety analysis and legal compliance.

STRICT RULES:
1. DIARIZATION: Identify speakers as (Speaker 1) (The Call Center Agent) and (Speaker 2) (The Caller/Customer).
2. NO CENSORSHIP: Do not sanitize or remove profanity, slurs, hate speech, or threats.
3. VERBATIM ACCURACY: Include stutters, false starts, grammatical errors.
4. FORMAT: Output transcript as dialogue turns with timestamps.

Example Output:
[00:00] Speaker 1: Hello, how can I help you?
[00:03] Speaker 2: I’m very upset, this is unacceptable!
"""
            ,
            uploaded_file
        ]
    )

    # Return the transcript as plain text
    return response.text
