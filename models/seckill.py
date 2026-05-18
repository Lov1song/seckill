from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class SeckillActivity(Base):
    __tablename__ = "seckill_activities"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer,ForeignKey("products.id"),nullable=False)
    seckill_price = Column(Float, nullable=False)   # 秒杀价
    total_stock = Column(Integer, nullable=False)    # 总库存
    available_stock = Column(Integer, nullable=False) # 剩余库存
    start_time = Column(DateTime, nullable=False)    # 开始时间
    end_time = Column(DateTime, nullable=False)      # 结束时间
    status = Column(String, default="pending")       # pending/active/ended
    created_at = Column(DateTime, server_default=func.now())

    #Relationship
    product = relationship("Product", back_populates="seckill_activities")
    orders = relationship("Order", back_populates="seckill_activity")