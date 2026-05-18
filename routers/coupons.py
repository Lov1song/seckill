from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from dependencies import get_current_user
from models.user import User
from models.coupon import Coupon, UserCoupon
from schemas.coupon import CouponCreate, CouponResponse, UserCouponResponse
from response import ApiResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/coupons", tags=["coupons"])

# 创建优惠券（管理员操作）
@router.post("/", response_model=ApiResponse)
def create_coupon(
    data: CouponCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    coupon = Coupon(
        name=data.name,
        type=data.type,
        condition=data.condition,
        discount=data.discount,
        expired_at=data.expired_at
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return ApiResponse.ok(data=CouponResponse.model_validate(coupon))

# 查询所有可用优惠券
@router.get("/", response_model=List[CouponResponse])
def get_coupons(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return db.query(Coupon).filter(Coupon.expired_at > now).all()

# 用户领取优惠券
@router.post("/{coupon_id}/claim", response_model=ApiResponse)
def claim_coupon(
    coupon_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查优惠券是否存在
    coupon = db.get(Coupon, coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    # 检查是否已过期
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if coupon.expired_at < now:
        raise HTTPException(status_code=400, detail="优惠券已过期")

    # 检查是否已领取
    existing = db.query(UserCoupon).filter(
        UserCoupon.user_id == current_user.id,
        UserCoupon.coupon_id == coupon_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已领取过该优惠券")

    # 领取
    user_coupon = UserCoupon(
        user_id=current_user.id,
        coupon_id=coupon_id
    )
    db.add(user_coupon)
    db.commit()
    return ApiResponse.ok(message="领取成功")

# 查询我的优惠券
@router.get("/my", response_model=List[UserCouponResponse])
def get_my_coupons(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy.orm import joinedload
    user_coupons = db.query(UserCoupon).options(
        joinedload(UserCoupon.coupon)
    ).filter(
        UserCoupon.user_id == current_user.id,
        UserCoupon.is_used == False
    ).all()
    return user_coupons