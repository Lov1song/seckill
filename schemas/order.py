from pydantic import BaseModel
from datetime import datetime

class OrderResponse(BaseModel):
    id: int
    user_id: int
    seckill_activity_id: int
    amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True