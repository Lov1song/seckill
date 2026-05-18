from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CouponCreate(BaseModel):
    name: str
    type: str
    condition: float
    discount: float
    expired_at: datetime
    scope: str = "global"           # 默认全场
    product_id: Optional[int] = None  # 指定商品时填

class CouponResponse(BaseModel):
    id: int
    name: str
    type: str
    condition: float
    discount: float
    expired_at: datetime
    scope: str
    product_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserCouponResponse(BaseModel):
    id: int
    coupon_id: int
    is_used: bool
    coupon: CouponResponse

    class Config:
        from_attributes = True