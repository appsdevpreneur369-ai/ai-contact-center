from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.tts_service import text_to_speech
import json

router = APIRouter()

llm_service = LLMService()
memory_service = MemoryService()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            session_id = payload["session_id"]
            user_message = payload["message"]

            await memory_service.save_message(session_id, "user", user_message)
            history = await memory_service.get_history(session_id)

            full_response = ""

            async for token in llm_service.generate_streaming_response(history):
                full_response += token
                await websocket.send_text(token)

            # Save assistant message
            await memory_service.save_message(session_id, "assistant", full_response)

            # 🔥 Generate TTS after streaming completes
            audio_filename = text_to_speech(full_response)

            # Send audio URL as JSON
            await websocket.send_text(
                json.dumps({
                    "type": "audio",
                    "audio_url": f"/audio/{audio_filename}"
                })
            )

            await websocket.send_text("[DONE]")

    except WebSocketDisconnect:
        print("Client disconnected")
