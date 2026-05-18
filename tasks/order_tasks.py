from celery_app import celery
from database import SessionLocal
from models.order import Order
from utils.redis_client import r
import logging
from models import user, product, seckill, order,coupon as order_model


logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def create_order_task(self, user_id: int, activity_id: int, amount: float):
    try:
        db = SessionLocal()
        
        # 创建订单
        order = Order(
            user_id=user_id,
            seckill_activity_id=activity_id,
            amount=amount,
            status="unpaid"
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        logger.info(f"订单创建成功：{order.id}")
        
        # 30分钟后自动取消未支付订单
        cancel_unpaid_order.apply_async(
            args=[order.id],
            countdown=1800
        )
        
        db.close()
        return order.id
        
    except Exception as exc:
        logger.error(f"订单创建失败：{exc}")
        raise self.retry(exc=exc)

@celery.task
def cancel_unpaid_order(order_id: int):
    db = SessionLocal()
    order = db.get(Order, order_id)
    
    if order and order.status == "unpaid":
        order.status = "cancelled"
        db.commit()
        
        # 释放 Redis 库存
        r.incr(f"seckill:stock:{order.seckill_activity_id}")
        logger.info(f"订单 {order_id} 超时取消，库存已释放")
    
    db.close()