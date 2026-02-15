from fastapi import APIRouter, UploadFile, File
import shutil
import os
from app.services.whisper_service import WhisperService

router = APIRouter()

whisper_service = WhisperService()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transcript = await whisper_service.transcribe(file_path)

    return {
        "filename": file.filename,
        "transcript": transcript
    }
