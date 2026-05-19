from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models.user import User
from models.seckill import SeckillActivity
from schemas.seckill import SeckillActivityCreate, SeckillActivityResponse, SeckillRequest
from utils.redis_client import (
    init_seckill_stock, deduct_stock,
    check_user_seckill, mark_user_seckill
)
from slowapi import Limiter
from slowapi.util import get_remote_address
from response import ApiResponse
from datetime import datetime, timezone
from typing import List
from tasks.order_tasks import create_order_task

router = APIRouter(prefix="/seckills", tags=["seckills"])

limiter = Limiter(key_func=get_remote_address)

# 创建秒杀活动（管理员操作）
@router.post("/activities",response_model=ApiResponse)
def create_activity(
    data:SeckillActivityCreate,
    current_user : User = Depends(get_current_user),
    db:Session = Depends(get_db)
):
    activity = SeckillActivity(
        product_id = data.product_id,
        seckill_price = data.seckill_price,
        total_stock = data.total_stock,
        available_stock = data.total_stock,
        start_time = data.start_time,
        end_time = data.end_time,
        status = "pending"
    )
    db.add(activity)
    db.flush()
    db.refresh(activity)

    #预热库存到Redis
    init_seckill_stock(activity.id,activity.total_stock)
    db.commit()

    return ApiResponse.ok(
        data=SeckillActivityResponse.model_validate(activity),
        message="秒杀活动创建成功"
    )

# 查询所有秒杀活动
@router.get("/activities", response_model=List[SeckillActivityResponse])
def get_activities(db: Session = Depends(get_db)):
    return db.query(SeckillActivity).all()


# ****用户参与秒杀****  添加限流装饰器
@router.post("/buy",response_model=ApiResponse)
@limiter.limit("5/minute")  # 每分钟限制5次请求
def seckill_buy(
    request:Request,# 必须加这个参数，限流器需要
    data:SeckillRequest,
    current_user:User = Depends(get_current_user),
    db:Session = Depends(get_db)
):
# 第一步：查询活动是否存在
    activity = db.get(SeckillActivity,data.activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    # 第二步：检查活动时间
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if now < activity.start_time:
        raise HTTPException(status_code=400, detail="活动还未开始")
    if now > activity.end_time:
        raise HTTPException(status_code=400, detail="活动已结束")
    
    # 第三步：检查用户是否已抢过（每人限购一次）
    if check_user_seckill(data.activity_id, current_user.id):
        raise HTTPException(status_code=400, detail="您已参与过该活动")

    # 第四步：Redis 原子扣减库存
    result = deduct_stock(data.activity_id)
    if result == -1:
        raise HTTPException(status_code=400, detail="活动库存未初始化")
    if result == 0:
        raise HTTPException(status_code=400, detail="已售罄")

    # 第五步：记录用户已抢购
    mark_user_seckill(data.activity_id, current_user.id)

    # 第六步：异步创建订单（后面接入 Celery）
    create_order_task.delay(current_user.id, data.activity_id, activity.seckill_price)

    return ApiResponse.ok(message="抢购成功，订单生成中")