"""
FastAPI 应用主入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core import get_settings, setup_logging, get_logger
from app.core.exceptions import AppException
from app.db import create_db_and_tables
from app.db.init_data import init_default_data
from app.db.session import async_session
from app.routers import (
    auth_router,
    users_router,
    teachers_router,
    students_router,
    courses_router,
    homeworks_router,
    submissions_router,
    folders_router,
    files_router,
)
from app.routers.ai import router as ai_router

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    setup_logging()
    logger.info("正在启动应用...")

    # 创建数据库表
    logger.info("正在创建数据库表...")
    await create_db_and_tables()

    # 初始化默认数据
    logger.info("正在初始化默认数据...")
    async with async_session() as session:
        await init_default_data(session)

    logger.info(f"应用启动完成！监听 http://{settings.host}:{settings.port}")
    logger.info(f"API 文档地址: http://localhost:{settings.port}/docs")

    yield

    # 关闭时
    logger.info("应用正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title="教育系统 API",
    description="教育系统后端 API 服务",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """处理应用异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "code": exc.code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "服务器内部错误",
            "code": "SYS_001"
        }
    )


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}


# 注册路由
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(teachers_router)
app.include_router(students_router)
app.include_router(courses_router)
app.include_router(homeworks_router)
app.include_router(submissions_router)
app.include_router(folders_router)
app.include_router(files_router)
app.include_router(ai_router)


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "教育系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
