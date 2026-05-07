"""传输服务器主程序"""
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import os

from config import settings
from database import init_database, close_database
import api_devices
import api_auth
import api_recordings
import api_config
from recording_scanner import scanner


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("=" * 60)
    logger.info("传输服务器启动")
    logger.info("=" * 60)

    # 初始化数据库
    await init_database()

    # 创建录像目录
    os.makedirs(settings.RECORDING_PATH, exist_ok=True)

    # 启动录像扫描服务（后台任务）
    scanner_task = asyncio.create_task(scanner.start())

    logger.info("服务器初始化完成")

    yield

    # 关闭时清理
    logger.info("开始清理资源...")
    scanner.stop()
    scanner_task.cancel()
    try:
        await scanner_task
    except asyncio.CancelledError:
        pass
    await close_database()
    logger.info("传输服务器已停止")


# 创建FastAPI应用
app = FastAPI(
    title="电厂巡检视频传输系统",
    description="端到端无线视频传输系统API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS（允许所有来源以支持局域网访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应该限制）
    allow_credentials=False,  # 允许所有来源时必须设为False
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(api_devices.router, prefix="/api/devices", tags=["设备管理"])
app.include_router(api_recordings.router, prefix="/api/recordings", tags=["录像管理"])
app.include_router(api_config.router)

# 静态文件服务（录像文件）
if os.path.exists(settings.RECORDING_PATH):
    app.mount("/recordings", StaticFiles(directory=settings.RECORDING_PATH), name="recordings")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "电厂巡检视频传输系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


def setup_logging():
    """配置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )
    logger.add(
        "logs/server_{time}.log",
        rotation="100 MB",
        retention="7 days",
        level=settings.LOG_LEVEL
    )


if __name__ == "__main__":
    import uvicorn

    # 配置日志
    setup_logging()

    # 启动服务器
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

