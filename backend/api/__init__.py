from fastapi import APIRouter
from .chat import router as chat_router
from .candyjar import router as candyjar_router

# 创建主路由器
api_router = APIRouter()

# 注册子路由器
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(candyjar_router, prefix="/candyjar", tags=["candyjar"])
