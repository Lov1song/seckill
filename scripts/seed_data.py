import sys
import os

# 把项目根目录加入 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import user, product, seckill, order, coupon
from faker import Faker
from database import SessionLocal
from models.product import Product
from models.seckill import SeckillActivity
from models.coupon import Coupon
from models.user import User
from models.coupon import UserCoupon
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
from models.order import Order

fake = Faker("zh_CN")
pwd_context = CryptContext(schemes=["bcrypt"])
db = SessionLocal()

# ===== 清空现有数据 =====
print("清空现有数据...")
db.query(UserCoupon).delete()
db.query(Coupon).delete()
db.query(Order).delete()          # 先删订单 外键约束问题
db.query(SeckillActivity).delete() # 再删秒杀活动
db.query(Product).delete()
db.query(User).delete()
db.commit()
# ===== 创建商品 =====
print("创建商品...")
products_data = [
    {"name": "华为 Mate 60 Pro", "description": "搭载麒麟9000S芯片，卫星通话", "price": 6999.0, "stock": 1000},
    {"name": "iPhone 15 Pro Max", "description": "A17 Pro芯片，钛金属边框", "price": 9999.0, "stock": 800},
    {"name": "小米14 Ultra", "description": "徕卡影像，骁龙8 Gen3", "price": 5999.0, "stock": 1200},
    {"name": "AirPods Pro 2", "description": "主动降噪，空间音频", "price": 1899.0, "stock": 2000},
    {"name": "华为 Watch GT4", "description": "智能手表，血氧监测", "price": 1488.0, "stock": 1500},
    {"name": "索尼 WH-1000XM5", "description": "旗舰降噪耳机", "price": 2499.0, "stock": 500},
    {"name": "iPad Pro 12.9", "description": "M2芯片，Liquid视网膜屏", "price": 8999.0, "stock": 300},
    {"name": "小米手环8 Pro", "description": "运动健康监测", "price": 399.0, "stock": 3000},
    {"name": "DJI Mini 4 Pro", "description": "4K无人机，全向避障", "price": 4799.0, "stock": 200},
    {"name": "机械革命 旷世16", "description": "RTX4070，游戏本", "price": 7999.0, "stock": 150},
]

products = []
for p in products_data:
    product = Product(**p)
    db.add(product)
    products.append(product)

db.flush()
for p in products:
    db.refresh(p)
print(f"创建了 {len(products)} 个商品")

# ===== 创建秒杀活动 =====
print("创建秒杀活动...")
now = datetime.now()

seckill_data = [
    # 正在进行的
    {
        "product": products[0],
        "seckill_price": 4999.0,
        "total_stock": 100,
        "start_time": now - timedelta(hours=1),
        "end_time": now + timedelta(hours=2),
        "status": "active"
    },
    {
        "product": products[1],
        "seckill_price": 7999.0,
        "total_stock": 50,
        "start_time": now - timedelta(minutes=30),
        "end_time": now + timedelta(hours=3),
        "status": "active"
    },
    {
        "product": products[3],
        "seckill_price": 999.0,
        "total_stock": 200,
        "start_time": now - timedelta(hours=2),
        "end_time": now + timedelta(hours=1),
        "status": "active"
    },
    # 即将开始的
    {
        "product": products[2],
        "seckill_price": 3999.0,
        "total_stock": 150,
        "start_time": now + timedelta(hours=1),
        "end_time": now + timedelta(hours=4),
        "status": "pending"
    },
    {
        "product": products[6],
        "seckill_price": 5999.0,
        "total_stock": 30,
        "start_time": now + timedelta(hours=2),
        "end_time": now + timedelta(hours=5),
        "status": "pending"
    },
]

activities = []
for s in seckill_data:
    product = s.pop("product")
    activity = SeckillActivity(
        product_id=product.id,
        available_stock=s["total_stock"],
        **s
    )
    db.add(activity)
    activities.append((activity, product))

db.flush()
for activity, _ in activities:
    db.refresh(activity)
print(f"创建了 {len(activities)} 个秒杀活动")

# ===== 创建优惠券 =====
print("创建优惠券...")
coupons_data = [
    # 全场券
    {
        "name": "全场满500减50",
        "type": "full_reduction",
        "condition": 500.0,
        "discount": 50.0,
        "expired_at": now + timedelta(days=30),
        "scope": "global",
        "product_id": None
    },
    {
        "name": "全场满1000减100",
        "type": "full_reduction",
        "condition": 1000.0,
        "discount": 100.0,
        "expired_at": now + timedelta(days=30),
        "scope": "global",
        "product_id": None
    },
    {
        "name": "全场九折券",
        "type": "discount",
        "condition": 0.0,
        "discount": 0.9,
        "expired_at": now + timedelta(days=15),
        "scope": "global",
        "product_id": None
    },
    # 指定商品券
    {
        "name": "华为手机专属满减券",
        "type": "full_reduction",
        "condition": 4000.0,
        "discount": 300.0,
        "expired_at": now + timedelta(days=30),
        "scope": "product",
        "product_id": products[0].id
    },
    {
        "name": "iPhone 专属九五折",
        "type": "discount",
        "condition": 0.0,
        "discount": 0.95,
        "expired_at": now + timedelta(days=30),
        "scope": "product",
        "product_id": products[1].id
    },
]

coupons = []
for c in coupons_data:
    coupon = Coupon(**c)
    db.add(coupon)
    coupons.append(coupon)

db.flush()
for c in coupons:
    db.refresh(c)
print(f"创建了 {len(coupons)} 张优惠券")

# ===== 创建用户 =====
print("创建用户...")
# 固定测试账号
test_user = User(
    name="测试用户",
    email="test@test.com",
    password=pwd_context.hash("Test1234")
)
db.add(test_user)
db.flush()
db.refresh(test_user)

# 给测试用户发放所有优惠券
for coupon in coupons:
    user_coupon = UserCoupon(
        user_id=test_user.id,
        coupon_id=coupon.id
    )
    db.add(user_coupon)

# 生成随机用户
random_users = []
for _ in range(20):
    user = User(
        name=fake.name(),
        email=fake.email(),
        password=pwd_context.hash("Test1234")
    )
    db.add(user)
    random_users.append(user)

db.flush()
for u in random_users:
    db.refresh(u)

# 随机给用户发放优惠券
for user in random_users:
    num_coupons = random.randint(1, 3)
    selected = random.sample(coupons, min(num_coupons, len(coupons)))
    for coupon in selected:
        user_coupon = UserCoupon(
            user_id=user.id,
            coupon_id=coupon.id
        )
        db.add(user_coupon)

print(f"创建了 {len(random_users) + 1} 个用户")

db.commit()

# ===== 预热 Redis 库存 =====
print("预热 Redis 库存...")
from utils.redis_client import init_seckill_stock, r

# 清空旧的秒杀数据
for key in r.scan_iter("seckill:*"):
    r.delete(key)

for activity, _ in activities:
    if activity.status == "active":
        init_seckill_stock(activity.id, activity.total_stock)
        print(f"活动 {activity.id} 库存已预热：{activity.total_stock}")

print("\n✅ 测试数据填充完成！")
print(f"测试账号：test@test.com")
print(f"密码：Test1234")
print(f"商品数：{len(products)}")
print(f"秒杀活动数：{len(activities)}")
print(f"优惠券数：{len(coupons)}")