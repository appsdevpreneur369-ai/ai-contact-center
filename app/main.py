from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.audio import router as audio_router  # Audio to Text End Point


app = FastAPI()
app.include_router(chat_router)
app.include_router(audio_router)

print("***** Om Si Ram AI Contact Center API *****")
