from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.audio import router as audio_router  # Audio to Text End Point
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ws_chat

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)
app.include_router(audio_router)
app.include_router(ws_chat.router)
os.makedirs("audio_outputs", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio_outputs"), name="audio")

print("***** Om Si Ram AI Contact Center API *****")
