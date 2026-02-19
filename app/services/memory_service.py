from sqlalchemy import select
from app.models.chat_models import ChatHistory
from app.db.database import AsyncSessionLocal


class MemoryService:
    MAX_CONTEXT_MESSAGES = 10  # configurable

    async def save_message(self, session_id: str, role: str, content: str):
        async with AsyncSessionLocal() as session:
            try:
                msg = ChatHistory(
                    session_id=session_id,
                    role=role,
                    content=content
                )
                session.add(msg)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def get_history(self, session_id: str):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ChatHistory)
                .where(ChatHistory.session_id == session_id)
                .order_by(ChatHistory.id)
            )
            records = result.scalars().all()

            # Convert ORM objects to dict format (important for LLM later)
            return [
                {
                    "role": r.role,
                    "content": r.content
                }
                for r in records
            ]

    async def get_all_history(self):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ChatHistory).order_by(ChatHistory.id)
            )
            records = result.scalars().all()

            return [
                {
                    "session_id": r.session_id,
                    "role": r.role,
                    "content": r.content
                }
                for r in records
            ]

    async def get_trimmed_history(self, session_id: str):
        history = await self.get_history(session_id)

        # Keep only last N messages (recent context)
        if len(history) > self.MAX_CONTEXT_MESSAGES:
            history = history[-self.MAX_CONTEXT_MESSAGES:]

        return history
