import re
from app.services.crm_service import CRMService

crm_service = CRMService()


class ToolRouter:

    def extract_order_id(self, text: str):
        match = re.search(r"\d{3,6}", text)
        return match.group(0) if match else None

    async def route(self, user_message: str, session_id: str):
        message_lower = user_message.lower()

        # Detect order intent
        if "order" in message_lower and (
            "status" in message_lower
            or "where" in message_lower
            or "track" in message_lower
        ):
            order_id = self.extract_order_id(user_message)

            # 🔹 Case 1: Order ID provided
            if order_id:
                order = await crm_service.get_order_by_id(order_id)
                return {
                    "intent": "order_status",
                    "order": order,
                    "order_id": order_id
                }

            # 🔹 Case 2: No ID → Fetch last order by customer
            last_order = await crm_service.get_last_order_by_customer(session_id)

            if last_order:
                return {
                    "intent": "last_order_status",
                    "order": last_order,
                    "order_id": last_order.order_id
                }

            # 🔹 Case 3: Ask for ID
            return {
                "intent": "ask_order_id",
                "order": None,
                "order_id": None
            }

        return None
