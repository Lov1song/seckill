from sqlalchemy import Column,Integer,String,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False)
    password = Column(String,nullable=False)
    create_at = Column(DateTime,server_default=func.now())

    orders = relationship("Order",back_populates="user")
    coupons = relationship("UserCoupon",back_populates="user")