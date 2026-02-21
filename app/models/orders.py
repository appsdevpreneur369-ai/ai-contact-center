from sqlalchemy import Column, String, Date, Integer, TIMESTAMP
from app.db.base import Base  # adjust if your base path differs


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, nullable=False)
    customer_id = Column(String, nullable=False)
    product_name = Column(String)
    status = Column(String)
    delivery_date = Column(Date)
    tracking_id = Column(String)
    created_at = Column(TIMESTAMP)
