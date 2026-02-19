import pyttsx3
import uuid
import os

def text_to_speech(text: str) -> str:
    engine = pyttsx3.init()

    file_name = f"{uuid.uuid4()}.mp3"
    file_path = os.path.join("audio_outputs", file_name)

    os.makedirs("audio_outputs", exist_ok=True)

    engine.save_to_file(text, file_path)
    engine.runAndWait()

    return file_path
