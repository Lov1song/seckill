from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from dependencies import get_current_user
from models.user import User
from models.product import Product
from schemas.product import ProductCreate, ProductResponse
from response import ApiResponse
import json
from utils.redis_client import r


router = APIRouter(prefix="/products", tags=["products"])

# 查询所有商品，不需要登录
@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

    # 查询单个商品，不需要登录
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
     # 先查 Redis
    cache_key = f"product:{product_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product

# 创建商品，需要登录 管理员权限 目前还没设置
@router.post("/", response_model=ApiResponse)
def create_product(
    data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ApiResponse.ok(data=ProductResponse.model_validate(product))

# 修改商品，需要登录
@router.put("/{product_id}", response_model=ApiResponse)
def update_product(
    product_id: int,
    data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    product.name = data.name
    product.description = data.description
    product.price = data.price
    product.stock = data.stock
    db.commit()
    db.refresh(product)

    #更新缓存
    r.delete(f"product:{product_id}")
    for key in r.scan_iter(f"search:products:*"):
        r.delete(key)

    return ApiResponse.ok(data=ProductResponse.model_validate(product))

# 删除商品，需要登录
@router.delete("/{product_id}", response_model=ApiResponse)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    db.delete(product)
    db.commit()

    # 删除缓存
    r.delete(f"product:{product_id}")
    for key in r.scan_iter("product:search:*"):
        r.delete(key)
    return ApiResponse.ok(message="删除成功")