from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    name:str
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    id:int
    name:str
    email:str
    #orm对象解析
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token:str
    token_type:str = "bearer"

    