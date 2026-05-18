from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from dependencies import get_current_user
from models.user import User
from models.order import Order
from schemas.order import OrderResponse
from response import ApiResponse

router = APIRouter(prefix="/orders", tags=["orders"])

# 查询当前用户所有订单
@router.get("/", response_model=List[OrderResponse])
def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

# 查询单个订单
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order

# 取消订单
@router.put("/{order_id}/cancel", response_model=ApiResponse)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "unpaid":
        raise HTTPException(status_code=400, detail="只能取消未支付的订单")

    order.status = "cancelled"
    db.commit()
    return ApiResponse.ok(message="订单已取消")