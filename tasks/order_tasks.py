from celery_app import celery
from database import SessionLocal
from models.order import Order
from utils.redis_client import r,init_seckill_stock
import logging
from models import user, product, seckill, order,coupon as order_model
from models.seckill import SeckillActivity
from datetime import datetime, timezone
logger = logging.getLogger(__name__)

@celery.task
def update_activity_status():
    db = SessionLocal()
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    #将时间活动改成active
    pending_activities = db.query(SeckillActivity).filter(
        SeckillActivity.status == "pending",
        SeckillActivity.start_time <= now
    ).all()

    for activity in pending_activities:
        activity.status = "active"
        #预热库存到Redis
        init_seckill_stock(activity.id,activity.total_stock)
        logger.info(f"活动 {activity.id} 已开始，库存已预热到Redis")

    #将过期活动改成expired
    active_activities = db.query(SeckillActivity).filter(
        SeckillActivity.status == "active",
        SeckillActivity.end_time <= now
    ).all()
    for activity in active_activities:
        activity.status = "ended"
        # 清除 Redis 库存
        r.delete(f"seckill:stock:{activity.id}")
        logger.info(f"活动 {activity.id} 结束，Redis 库存已清除")
    db.commit()
    db.close()

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
        #同步更新数据库库存
        activity = db.get(SeckillActivity,activity_id)
        if activity and activity.avavilable_stock > 0:
            activity.avavilable_stock -= 1
            logger.info(f"库存扣减成功，剩余库存：{activity.avavilable_stock}")

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
        
        # 释放数据库库存
        activity = db.get(SeckillActivity, order.seckill_activity_id)
        if activity:
            activity.available_stock += 1
            logger.info(f"订单 {order_id} 取消，数据库库存释放：{activity.available_stock}")
        
        db.commit()
        # 释放 Redis 库存
        r.incr(f"seckill:stock:{order.seckill_activity_id}")
        logger.info(f"订单 {order_id} 超时取消，库存已释放")
    
    db.close()