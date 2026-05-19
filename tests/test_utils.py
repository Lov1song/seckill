import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers.users import hash_password,verify_password,create_token
from jose import jwt

def test_hash_and_verify_password():
    password = "Test1234"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("WrongPassword", hashed) == False

# 测试 Token 生成
def test_create_token():
    token = create_token(user_id=1)
    
    # Token 不为空
    assert token is not None
    
    # Token 能解码
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
    assert payload["user_id"] == 1