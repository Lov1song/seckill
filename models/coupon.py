from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)      # full_reduction / discount
    condition = Column(Float, nullable=False)
    discount = Column(Float, nullable=False)
    expired_at = Column(DateTime, nullable=False)
    scope = Column(String, default="global")   # global / product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # scope=product 时才有值

    user_coupons = relationship("UserCoupon", back_populates="coupon")
    product = relationship("Product", backref="coupons")

class UserCoupon(Base):
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="coupons")
    coupon = relationship("Coupon", back_populates="user_coupons")