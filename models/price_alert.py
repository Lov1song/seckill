#价格预警表 -> 辅助agent进行价格预警

from sqlalchemy import Column,Boolean ,Integer, String, Float, DateTime,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class PriceAlert(Base):
    __tablename__ = 'price_alerts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    target_price = Column(Float, nullable=False) #目标价格
    is_triggered = Column(Boolean, default=0) #是否已触发预警
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    triggered_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")
    product = relationship("Product")
    