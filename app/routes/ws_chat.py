from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.tts_service import text_to_speech
from app.services.tool_router import ToolRouter
import json


router = APIRouter()

llm_service = LLMService()
memory_service = MemoryService()
tool_router = ToolRouter()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            session_id = payload["session_id"]
            user_message = payload["message"]

            # 1️⃣ Save user message
            await memory_service.save_message(session_id, "user", user_message)

            # 2️⃣ TOOL DETECTION (Pass session_id)
            tool_result = await tool_router.route(user_message, session_id)

            if tool_result:
                intent = tool_result.get("intent")
                order = tool_result.get("order")
                order_id = tool_result.get("order_id")

                # 🔹 Case 1: Order Found
                if intent in ["order_status", "last_order_status"] and order:
                    full_response = (
                        f"Thank you for contacting support. "
                        f"Your order #{order.order_id} "
                        f"({order.product_name}) is currently {order.status}. "
                        f"Expected delivery date is {order.delivery_date}. "
                    )

                    if order.tracking_id:
                        full_response += f"Tracking ID is {order.tracking_id}."

                # 🔹 Case 2: Ask for Order ID
                elif intent == "ask_order_id":
                    full_response = (
                        "Sure, I can help with your order status. "
                        "Could you please provide your order ID?"
                    )

                # 🔹 Case 3: Invalid Order ID
                else:
                    full_response = (
                        f"Sorry, I could not find any order with ID {order_id}."
                    )

                # Save assistant response
                await memory_service.save_message(
                    session_id, "assistant", full_response
                )

                # Stream response (typing effect)
                for char in full_response:
                    await websocket.send_text(char)

                # Generate TTS
                audio_filename = text_to_speech(full_response)

                await websocket.send_text(
                    json.dumps({
                        "type": "audio",
                        "audio_url": f"/audio/{audio_filename}"
                    })
                )

                await websocket.send_text("[DONE]")
                continue  # 🚀 Skip LLM

            # 3️⃣ No tool match → Use LLM
            history = await memory_service.get_trimmed_history(session_id)

            full_response = ""

            async for token in llm_service.generate_streaming_response(history):
                full_response += token
                await websocket.send_text(token)

            # Save assistant message
            await memory_service.save_message(
                session_id, "assistant", full_response
            )

            # Generate TTS
            audio_filename = text_to_speech(full_response)

            await websocket.send_text(
                json.dumps({
                    "type": "audio",
                    "audio_url": f"/audio/{audio_filename}"
                })
            )

            await websocket.send_text("[DONE]")

    except WebSocketDisconnect:
        print("Client disconnected")
