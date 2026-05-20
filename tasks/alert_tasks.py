from celery_app import celery
from database import SessionLocal
from models import user, product, seckill, order, coupon, price_alert
from models.price_alert import PriceAlert
from models.product import Product
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

@celery.task
def check_price_alerts():
    """每小时检查价格预警"""
    db = SessionLocal()

    # 查找未触发的预警
    alerts = db.query(PriceAlert).filter(
        PriceAlert.is_triggered == False
    ).all()

    triggered_count = 0

    for alert in alerts:
        product = db.get(Product, alert.product_id)
        if not product:
            continue

        # 检查是否有秒杀活动
        from models.seckill import SeckillActivity
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        seckill = db.query(SeckillActivity).filter(
            SeckillActivity.product_id == product.id,
            SeckillActivity.status == "active",
            SeckillActivity.start_time <= now,
            SeckillActivity.end_time >= now
        ).first()

        current_price = seckill.seckill_price if seckill else product.price

        if current_price <= alert.target_price:
            alert.is_triggered = True
            alert.triggered_at = datetime.now(timezone.utc).replace(tzinfo=None)
            triggered_count += 1

            logger.info(
                f"价格预警触发：用户{alert.user_id} "
                f"商品{product.name} 当前价{current_price}元 "
                f"目标价{alert.target_price}元"
            )

    db.commit()
    db.close()

    logger.info(f"价格检查完成：{len(alerts)} 个预警，{triggered_count} 个触发")