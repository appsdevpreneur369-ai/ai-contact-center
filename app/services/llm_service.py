import httpx
import time
import json


class LLMService:

    def __init__(self, model: str = "gemma:2b"):
        self.base_url = "http://localhost:11434/api/chat"
        self.model = model

    async def generate_response(self, messages: list) -> str:

        # 🔹 1️⃣ Add System Prompt
        system_prompt = {
            "role": "system",
            "content": (
                "You are a professional AI customer support assistant. "
                "Answer clearly and concisely using the conversation history."
            )
        }

        # 🔹 2️⃣ Trim History (last N messages only)
        MAX_MESSAGES = 10
        trimmed_history = messages[-MAX_MESSAGES:]

        # Combine system + history
        final_messages = [system_prompt] + trimmed_history

        payload = {
            "model": self.model,
            "messages": final_messages,
            "stream": False
        }

        try:
            start_time = time.time()

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self.base_url, json=payload)

            response.raise_for_status()

            result = response.json()

            end_time = time.time()

            # 🔹 3️⃣ Latency Logging
            print(f"LLM Response Time: {end_time - start_time:.2f} seconds")

            return result["message"]["content"].strip()

        except Exception as e:
            return f"LLM Error: {str(e)}"

    async def generate_streaming_response(self, history):

        # 🔹 Build prompt manually
        prompt = ""

        for msg in history:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"

        prompt += "Assistant: "

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma:2b",
                    "prompt": prompt,
                    "stream": True
                },
            ) as response:

                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]