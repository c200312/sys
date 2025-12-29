"""
AI Provider 基类
定义 AI 服务的接口规范
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.schemas.ai import (
    PPTGenerateRequest,
    PPTGenerateResponse,
    ContentGenerateRequest,
    ContentGenerateResponse,
    ContentEditRequest,
    ContentEditResponse,
    ChatRequest,
    ChatResponse,
)


class AIProvider(ABC):
    """AI Provider 抽象基类"""

    @abstractmethod
    async def generate_ppt(self, request: PPTGenerateRequest) -> PPTGenerateResponse:
        """生成 PPT 内容"""
        pass

    @abstractmethod
    async def generate_content(self, request: ContentGenerateRequest) -> ContentGenerateResponse:
        """生成教学资源内容"""
        pass

    @abstractmethod
    async def edit_content(self, request: ContentEditRequest) -> ContentEditResponse:
        """AI 二改内容"""
        pass

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """聊天对话"""
        pass
