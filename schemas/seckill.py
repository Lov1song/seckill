from pydantic import BaseModel
from datetime import datetime

class SeckillActivityCreate(BaseModel):
    product_id: int
    seckill_price: float
    total_stock: int
    start_time: datetime
    end_time: datetime

class SeckillActivityResponse(BaseModel):
    id: int
    product_id: int
    seckill_price: float
    total_stock: int
    available_stock: int
    start_time: datetime
    end_time: datetime
    status: str

    class Config:
        from_attributes = True

class SeckillRequest(BaseModel):
    activity_id: int