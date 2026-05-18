from database import engine
from utils.redis_client import r, check_redis
from sqlalchemy import text

# 测试数据库
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("PostgreSQL 连接成功 ✅")

# 测试 Redis
if check_redis():
    print("Redis 连接成功 ✅")