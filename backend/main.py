from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.config import settings
from api import api_router
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to LLM App Platform",
        "version": settings.app_version,
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

# 列出所有技能
@app.get("/skills")
async def list_skills():
    """列出所有技能"""
    from core.chat_orchestrator import chat_orchestrator
    return {
        "skills": chat_orchestrator.list_skills(),
        "timestamp": "2026-03-04"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
