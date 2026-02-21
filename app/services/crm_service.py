from sqlalchemy import select, desc
from app.models.orders import Order
from app.db.database import get_async_session


class CRMService:

    async def get_order_by_id(self, order_id: str):
        async for session in get_async_session():
            result = await session.execute(
                select(Order).where(Order.order_id == order_id)
            )
            return result.scalar_one_or_none()

    async def get_last_order_by_customer(self, customer_id: str):
        async for session in get_async_session():
            result = await session.execute(
                select(Order)
                .where(Order.customer_id == customer_id)
                .order_by(desc(Order.created_at))
                .limit(1)
            )
            return result.scalar_one_or_none()
