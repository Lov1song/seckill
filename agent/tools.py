from langchain_core.tools import tool
from database import SessionLocal
from models.product import Product
from models.seckill import SeckillActivity
from models.coupon import Coupon, UserCoupon
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from utils.redis_client import r
import logging
# 用 BaseModel 定义工具参数，避免序列化问题
class SearchProductsInput(BaseModel):
    keyword: str

class GetSeckillInput(BaseModel):
    product_id: Optional[int] = None

class GetUserCouponsInput(BaseModel):
    user_id: int

class CalculateBestDealInput(BaseModel):
    original_price: float
    seckill_price: float
    user_id: int
    product_id: int

logger = logging.getLogger(__name__)

@tool(args_schema=SearchProductsInput)
def search_products(keyword:str) -> str:
    """搜索商品信息，输入关键词，返回匹配的商品列表"""

    #先查Redis缓存
    cache_key = f"search:products:{keyword}"
    cached = r.get(cache_key)
    if cached:
        logger.info(f"从Redis缓存获取搜索结果，关键词：{keyword}")
        return cached

    db = SessionLocal()
    products = db.query(Product).filter(Product.name.contains(keyword)).all()
    db.close()

    if not products:
        return "未找到相关商品"
    result = []
    for p in products:
        result.append(f"商品ID:{p.id} | 名称:{p.name} | 原价:{p.price}元 | 库存:{p.stock}")
    return "\n".join(result)

@tool(args_schema=GetSeckillInput)
def get_seckill_activities(product_id: Optional[int] = None) -> str:
    """查询正在进行的秒杀活动，可以指定商品ID筛选"""
    db = SessionLocal()
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    query = db.query(SeckillActivity).filter(
        SeckillActivity.start_time <= now,
        SeckillActivity.end_time >= now,
        SeckillActivity.available_stock > 0
    )

    if product_id:
        query = query.filter(SeckillActivity.product_id == product_id)

    activities = query.all()
    db.close()

    if not activities:
        return "当前没有正在进行的秒杀活动"

    result = []
    for a in activities:
        result.append(
            f"活动ID:{a.id} | 商品ID:{a.product_id} | "
            f"秒杀价:{a.seckill_price}元 | 剩余库存:{a.available_stock} | "
            f"结束时间:{a.end_time}"
        )
    return "\n".join(result)


@tool(args_schema=GetUserCouponsInput)
def get_user_coupons(user_id: int) -> str:
    """查询用户可用的优惠券列表"""
    from sqlalchemy.orm import joinedload
    db = SessionLocal()
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    user_coupons = db.query(UserCoupon).options(
        joinedload(UserCoupon.coupon)  # 预加载 coupon
    ).join(Coupon).filter(
        UserCoupon.user_id == user_id,
        UserCoupon.is_used == False,
        Coupon.expired_at > now
    ).all()

    result = []
    for uc in user_coupons:
        c = uc.coupon
        if c.type == "full_reduction":
            desc = f"满{c.condition}减{c.discount}元"
        else:
            desc = f"满{c.condition}元打{c.discount * 10}折"
        scope = "全场通用" if c.scope == "global" else f"仅限商品ID:{c.product_id}"
        result.append(f"券ID:{uc.id} | {c.name} | {desc} | {scope}")

    db.close()

    if not result:
        return "用户暂无可用优惠券"
    return "\n".join(result)

@tool(args_schema=CalculateBestDealInput)
def calculate_best_deal(original_price: float, seckill_price: float, user_id: int, product_id: int) -> str:
    """计算最优优惠方案，输入原价、秒杀价、用户ID和商品ID，返回最优购买方案"""
    from sqlalchemy.orm import joinedload
    db = SessionLocal()
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    user_coupons = db.query(UserCoupon).options(
        joinedload(UserCoupon.coupon)  # 预加载 coupon
    ).join(Coupon).filter(
        UserCoupon.user_id == user_id,
        UserCoupon.is_used == False,
        Coupon.expired_at > now
    ).all()

    base_price = seckill_price if seckill_price > 0 else original_price
    best_saving = 0
    best_coupon = None
    best_final_price = base_price

    for uc in user_coupons:
        c = uc.coupon
        if c.scope == "product" and c.product_id != product_id:
            continue
        if base_price < c.condition:
            continue

        if c.type == "full_reduction":
            saving = c.discount
            final_price = base_price - saving
        else:
            final_price = base_price * c.discount
            saving = base_price - final_price

        if saving > best_saving:
            best_saving = saving
            best_coupon = c
            best_final_price = final_price

    db.close()

    total_saving = original_price - best_final_price

    if best_coupon:
        return (
            f"最优方案：\n"
            f"原价：{original_price}元\n"
            f"秒杀价：{base_price}元\n"
            f"使用券：{best_coupon.name}\n"
            f"最终价格：{best_final_price:.2f}元\n"
            f"共节省：{total_saving:.2f}元"
        )
    else:
        return (
            f"最优方案：\n"
            f"原价：{original_price}元\n"
            f"秒杀价：{base_price}元\n"
            f"暂无可用优惠券\n"
            f"共节省：{original_price - base_price:.2f}元"
        )