import os
from services.speech_to_text import transcribe_call
from ai.hate_detector import detect_hate_from_textfile
from datetime import datetime

# ---------- CONFIG ----------
agent_id = "agent_12"
audio_file = "test_audio.mp3"  # path to your test audio
transcript_dir = f"data/transcripts/{agent_id}"
os.makedirs(transcript_dir, exist_ok=True)

# ---------- STEP 1: Transcribe audio ----------
print("Transcribing audio...")
transcript_text = transcribe_call(audio_file)
print("Transcript done!\n")
print(transcript_text)
print("\n---\n")

# ---------- STEP 2: Save transcript as TXT ----------
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
conversation_id = f"conv_{timestamp}"
txt_path = os.path.join(transcript_dir, f"{conversation_id}.txt")

with open(txt_path, "w", encoding="utf-8") as f:
    f.write(transcript_text)

print(f"Transcript saved to {txt_path}\n")

# ---------- STEP 3: Run hate detector ----------
print("Running hate detector...")
report = detect_hate_from_textfile(txt_path)

# ---------- STEP 4: Show results ----------
print("Hate detection report:")
print(report)
