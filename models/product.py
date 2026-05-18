from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False)
    description = Column(String)
    price = Column(Float,nullable=False)
    stock = Column(Integer,nullable=False)
    created_at = Column(DateTime,server_default=func.now())

    #Relationship
    seckill_activities = relationship("SeckillActivity",back_populates="product")