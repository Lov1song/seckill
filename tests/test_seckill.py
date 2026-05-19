import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from utils.redis_client import r, init_seckill_stock, deduct_stock, check_user_seckill, mark_user_seckill

def setup_function():
    """每个测试前清空 Redis 测试数据"""
    r.delete("seckill:stock:999")
    r.delete("seckill:users:999")

def test_init_stock():
    """测试库存初始化"""
    init_seckill_stock(999, 100)
    stock = r.get("seckill:stock:999")
    assert stock == "100"

def test_deduct_stock_success():
    """测试正常扣减库存"""
    init_seckill_stock(999, 10)
    result = deduct_stock(999)
    assert result == 1  # 扣减成功
    assert r.get("seckill:stock:999") == "9"

def test_deduct_stock_empty():
    """测试库存为0时扣减失败"""
    init_seckill_stock(999, 0)
    result = deduct_stock(999)
    assert result == 0  # 扣减失败

def test_deduct_stock_not_exist():
    """测试活动不存在"""
    result = deduct_stock(99999)
    assert result == -1  # 活动不存在

def test_prevent_oversell():
    """测试防超卖：100个请求只能成功10个"""
    init_seckill_stock(999, 10)
    
    success_count = 0
    for i in range(100):
        result = deduct_stock(999)
        if result == 1:
            success_count += 1
    
    assert success_count == 10  # 只有10个成功
    assert r.get("seckill:stock:999") == "0"

def test_user_limit():
    """测试每人限购一次"""
    init_seckill_stock(999, 100)
    
    # 第一次抢购
    assert check_user_seckill(999, 1) == False  # 没有抢过
    mark_user_seckill(999, 1)
    assert check_user_seckill(999, 1) == True   # 已经抢过