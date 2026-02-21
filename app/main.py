from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api.chat import router as chat_router
from app.api.audio import router as audio_router
from app.routes import ws_chat
from app.db.base import Base
from app.db.database import engine
from app.models.orders import Order  # ensure model is imported


# 🔥 Modern Lifespan Handler (Replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 Startup logic
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables ensured.")
    print("***** Om Si Ram AI Contact Center API *****")

    yield

    # 🔹 Shutdown logic (optional)
    print("🔻 Shutting down AI Contact Center API...")


app = FastAPI(lifespan=lifespan)

# 🔹 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Routers
app.include_router(chat_router)
app.include_router(audio_router)
app.include_router(ws_chat.router)

# 🔹 Static Audio Mount
os.makedirs("audio_outputs", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio_outputs"), name="audio")
