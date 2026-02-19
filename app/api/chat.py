from fastapi import APIRouter
from pydantic import BaseModel
from app.services.memory_service import MemoryService
from app.services.llm_service import LLMService
from app.services.tts_service import text_to_speech

router = APIRouter()

memory_service = MemoryService()
llm_service = LLMService()


# 🔹 Request Model (Professional)
class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def chat(payload: ChatRequest):

    session_id = payload.session_id
    user_message = payload.message

    # 1️⃣ Save user message
    await memory_service.save_message(session_id, "user", user_message)

    # 2️⃣ Fetch history
    # //history = await memory_service.get_history(session_id)
    history = await memory_service.get_trimmed_history(session_id)

    # 3️⃣ Generate LLM response
    response = await llm_service.generate_response(history)

    # 4️⃣ Save assistant message
    await memory_service.save_message(session_id, "assistant", response)

    # 5️⃣ Convert LLM response to speech
    audio_filename = text_to_speech(response)

    return {
        "response": response,
        "audio_url": f"/audio/{audio_filename}"
    }


@router.get("/chat/{session_id}")
async def get_chat(session_id: str):

    # history = await memory_service.get_history(session_id)
    history = await memory_service.get_trimmed_history(session_id)

    return {
        "status": "OK",
        "total_messages": len(history),
        "history": history
    }


@router.get("/all-history")
async def all_history():

    data = await memory_service.get_all_history()

    return {
        "status": "OK",
        "data": data
    }
