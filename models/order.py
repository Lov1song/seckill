from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seckill_activity_id = Column(Integer, ForeignKey("seckill_activities.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="unpaid")  # unpaid/paid/cancelled
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="orders")
    seckill_activity = relationship("SeckillActivity", back_populates="orders")