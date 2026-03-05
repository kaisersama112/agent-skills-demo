import uuid
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import api_router
from config.config import settings
from core.telemetry import log_event

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or f"trace-{uuid.uuid4().hex[:12]}"
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    trace_id = getattr(request.state, "trace_id", "")
    log_event("http_exception", trace_id=trace_id, path=request.url.path, status_code=exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "status": "error",
                "error_code": "http_exception",
                "message": exc.detail,
                "trace_id": trace_id,
            },
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "")
    log_event("unhandled_exception", trace_id=trace_id, path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "status": "error",
                "error_code": "internal_error",
                "message": "Internal server error",
                "trace_id": trace_id,
            },
            "timestamp": datetime.utcnow().isoformat(),
        },
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


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to LLM App Platform",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/skills")
async def list_skills():
    """列出所有技能"""
    from core.chat_orchestrator import chat_orchestrator

    return {
        "skills": chat_orchestrator.list_skills(),
        "timestamp": "2026-03-04",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
