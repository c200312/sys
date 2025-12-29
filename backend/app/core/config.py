"""
核心配置模块
加载环境变量并提供配置对象
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./edu_system.db"

    # JWT 配置
    secret_key: str = "dev-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24小时

    # CORS 配置
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = True

    # AI 配置 (预留)
    ai_provider: str = "mock"
    ai_api_key: str = ""
    ai_model: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """将逗号分隔的 CORS origins 转为列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取缓存的配置对象"""
    return Settings()
