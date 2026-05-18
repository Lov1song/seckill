from fastapi import Depends,HTTPException,Header
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt,JWTError
from database import get_db
from models.user import User
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db:Session = Depends(get_db)
) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        user_id = payload.get("user_id")
    except(JWTError,IndexError):
        raise HTTPException(status_code=401, detail="Token 无效或已过期")
    
    user = db.get(User,user_id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user