"""
日志配置模块
"""
import logging
import sys

from app.core.config import get_settings

settings = get_settings()


def setup_logging():
    """配置日志"""
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # 配置根日志
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # 降低第三方库日志级别
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取命名日志器"""
    return logging.getLogger(name)
