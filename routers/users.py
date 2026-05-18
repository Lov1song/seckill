from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate,UserResponse,TokenResponse
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
from jose import jwt
import os

router = APIRouter(prefix="/users",tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 300

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain:str,hashed:str) -> bool:
    return pwd_context.verify(plain,hashed)

def create_token(user_id:int) -> str:
    payload = {
        "user_id" : user_id,
        "exp" : datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

@router.post("/register",response_model=UserResponse)
def regsiter(
    user_data:UserCreate,
    db:Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400,detail="邮箱已存在")
    
    user = User(
        name = user_data.name,
        email = user_data.email,
        password = hash_password(user_data.password) #不能明文存入数据库
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login",response_model=TokenResponse)
def login(
    email:str,
    password:str,
    db:Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password,user.password):
        raise HTTPException(status_code=404,detail="邮箱或者密码错误")
    
    token = create_token(user.id)
    return TokenResponse(access_token=token)