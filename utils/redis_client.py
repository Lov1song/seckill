import redis
import os

r = redis.Redis(
    host=os.getenv("REDIS_HOST","localhost"),
    port=int(os.getenv("REDIS_PORT",6379)),
    decode_responses=True
)

def check_redis():
    try:
        r.ping()
        return True
    except:
        return False
    
#初始化秒杀库存到 Redis
def init_seckill_stock(activity_id:int,stock:int):
    r.set(f"seckill:stock:{activity_id}",stock)

# Lua 脚本原子扣减库存
DEDUCT_STOCK_SCRIPT = """
local stock = redis.call('get', KEYS[1])
if stock == false then
    return -1  -- 活动不存在
end
if tonumber(stock) <= 0 then
    return 0   -- 已售罄
end
redis.call('decr', KEYS[1])
return 1       -- 扣减成功
"""

def deduct_stock(activity_id:int) -> int:
    result = r.eval(DEDUCT_STOCK_SCRIPT,1,f"seckill:stock:{activity_id}")
    return result

# 检查用户是否已经抢过
def check_user_seckill(activity_id:int,user_id:int) -> bool:
    return r.sismember(f"seckill:users:{activity_id}",user_id)

# 记录用户已抢购
def mark_user_seckill(activity_id: int, user_id: int):
    r.sadd(f"seckill:users:{activity_id}", user_id)