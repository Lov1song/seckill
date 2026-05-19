import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register():
    """测试用户注册"""
    response = client.post("/users/register", json={
        "name": "测试用户",
        "email": "pytest@test.com",
        "password": "Test1234"
    })
    # 注册成功或邮箱已存在都算通过
    assert response.status_code in [200, 400]

def test_login_success():
    """测试登录成功"""
    # 先注册
    client.post("/users/register", json={
        "name": "登录测试",
        "email": "login_test@test.com",
        "password": "Test1234"
    })
    
    # 再登录
    response = client.post("/users/login", params={
        "email": "login_test@test.com",
        "password": "Test1234"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    """测试密码错误"""
    response = client.post("/users/login", params={
        "email": "test@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_products():
    """测试查询商品列表"""
    response = client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_product_not_found():
    """测试查询不存在的商品"""
    response = client.get("/products/99999")
    assert response.status_code == 404

def test_seckill_without_token():
    """测试未登录不能参与秒杀"""
    response = client.post("/seckill/buy", json={"activity_id": 1})
    assert response.status_code == 403