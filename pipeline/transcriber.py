import os
from groq import Groq

MAX_FILE_SIZE = 24 * 1024 * 1024  # 24MB (Groq limit is 25MB)

def transcribe_audio(audio_path):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set.")

    if os.path.getsize(audio_path) > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {audio_path}")

    client = Groq(api_key=api_key)

    with open(audio_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), f.read()),
            model="whisper-large-v3",
            response_format="text",
        )

    return transcription

def transcribe_all(audio_files):
    transcripts = []
    for path in audio_files:
        try:
            text = transcribe_audio(path)
            if text and text.strip():
                transcripts.append({"file": path, "text": text.strip()})
        except Exception as e:
            print(f"Skipping {path}: {e}")
    return transcripts
