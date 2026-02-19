import httpx
import time
import json


class LLMService:

    def __init__(self, model: str = "gemma:2b"):
        self.base_url = "http://localhost:11434/api/chat"
        self.generate_url = "http://localhost:11434/api/generate"
        self.model = model
        self.MAX_MESSAGES = 10  # Context window limit

    # 🔹 NEW: Intelligent Context Builder (Day 6 Core)
    def build_context_messages(self, history: list) -> list:
        """
        Builds structured messages for Ollama chat API
        with system prompt + trimmed history
        """

        system_prompt = {
            "role": "system",
            "content": (
                "You are an AI Voice Customer Support Agent for a Contact Center. "
                "Be polite, concise, professional, and context-aware. "
                "Use conversation history to answer accurately."
            )
        }

        # 🔹 Intelligent trimming (last N messages only)
        trimmed_history = history[-self.MAX_MESSAGES:]

        return [system_prompt] + trimmed_history

    # 🔹 OPTIONAL (Advanced Prompt Style - for /generate endpoint)
    def build_context_prompt(self, history: list) -> str:
        system_prompt = (
            "You are an AI Voice Customer Support Agent. "
            "Be polite, concise, and helpful.\n\n"
        )

        conversation = ""

        for msg in history[-self.MAX_MESSAGES:]:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                conversation += f"Customer: {content}\n"
            elif role == "assistant":
                conversation += f"Agent: {content}\n"

        final_prompt = system_prompt + conversation + "Agent: "
        return final_prompt

    # 🔹 Non-Streaming Response (REST Chat)
    async def generate_response(self, messages: list) -> str:

        # ✅ Use intelligent context builder
        final_messages = self.build_context_messages(messages)

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
            print(f"LLM Response Time: {end_time - start_time:.2f} seconds")

            return result["message"]["content"].strip()

        except Exception as e:
            return f"LLM Error: {str(e)}"

    # 🔥 Streaming Response (WebSocket - Day 4 + Day 6 optimized)
    async def generate_streaming_response(self, history):

        # ✅ CRITICAL: Use structured context prompt (Day 6)
        prompt = self.build_context_prompt(history)

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    self.generate_url,
                    json={
                        "model": self.model,  # 🔹 FIX: use self.model (not hardcoded)
                        "prompt": prompt,
                        "stream": True
                    },
                ) as response:

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        try:
                            data = json.loads(line)

                            # Ollama streaming token
                            if "response" in data:
                                yield data["response"]

                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            yield f"\n[Streaming Error: {str(e)}]"
