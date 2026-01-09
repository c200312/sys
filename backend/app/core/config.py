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

    # AI PPT 生成配置
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str = ""
    aippt_port: int = 8002
    ai_ppt_model: str = ""

    # AI 写作服务配置
    aiwriting_port: int = 8003
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    aiwriting_model: str = "gpt-4o"

    # AI RAG 服务配置
    airag_port: int = 8004
    airag_model: str = "gpt-4o"

    # AI 评分服务配置
    aigrading_port: int = 8005

    # MinerU API 配置 (PDF/DOCX 解析)
    mineru_api_token: str = ""

    # 阿里云百炼 API 配置 (PPT 图片解析)
    dashscope_api_key: str = ""

    # MinIO 对象存储配置
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket: str = "edu-system"
    minio_secure: bool = False

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
