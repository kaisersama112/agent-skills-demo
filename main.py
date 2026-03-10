from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import api
from config import settings
import os

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建sandbox目录
os.makedirs(os.path.join(os.getcwd(), "sandbox", "apps"), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), "sandbox", "images"), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), "sandbox", "svgs"), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), "sandbox", "static"), exist_ok=True)

# 挂载静态文件服务
app.mount("/apps", StaticFiles(directory=os.path.join(os.getcwd(), "sandbox", "apps"), html=True), name="apps")
app.mount("/images", StaticFiles(directory=os.path.join(os.getcwd(), "sandbox", "images")), name="images")
app.mount("/svgs", StaticFiles(directory=os.path.join(os.getcwd(), "sandbox", "svgs")), name="svgs")
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "sandbox", "static")), name="static")

app.include_router(api.router, prefix="/api/v1", tags=["api"])


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running"
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
    