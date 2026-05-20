from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import users,seckills,products,orders,coupons,agents
from models import user, product, seckill, order,coupon,price_alert
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
load_dotenv()

app = FastAPI(title="智能电商秒杀系统")

#创造限流器
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

#限流超出的处理
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(seckills.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(coupons.router)
app.include_router(agents.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request:Request,exc:HTTPException,):
    return JSONResponse(
        status_code=exc.status_code,
        content = {"code":exc.status_code,"message":exc.detail,"data":None}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request:Request,exc:Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None}
    )