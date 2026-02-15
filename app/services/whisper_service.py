import os
import whisper

os.environ["PATH"] += os.pathsep + r"D:\ffmpeg\bin"

class WhisperService:

    def __init__(self):
        self.model = whisper.load_model("base")

    async def transcribe(self, file_path: str):
        result = self.model.transcribe(file_path)
        return result["text"]
