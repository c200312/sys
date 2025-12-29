"""
AI 相关 Schema
注意：AI 接口目前仅保留占位，逻辑不实现
"""
from typing import Optional, List

from pydantic import BaseModel, Field


# ============= PPT 生成 =============

class PPTGenerateRequest(BaseModel):
    """PPT 生成请求"""
    title: str = Field(..., min_length=1, max_length=200)
    requirements: str = Field(..., min_length=1)


class PPTGenerateResponse(BaseModel):
    """PPT 生成响应"""
    content: str  # Markdown/Marp 格式
    title: str


# ============= 教学资源生成 =============

class ReferenceFile(BaseModel):
    """参考资料文件"""
    name: str
    content: str  # Base64 或文本


class ContentGenerateRequest(BaseModel):
    """教学资源生成请求"""
    title: str = Field(..., min_length=1, max_length=200)
    requirements: str = Field(..., min_length=1)
    references: Optional[List[ReferenceFile]] = None


class ContentGenerateResponse(BaseModel):
    """教学资源生成响应"""
    content: str  # Markdown 格式
    title: str


# ============= AI 二改 =============

class ContentEditRequest(BaseModel):
    """AI 二改请求"""
    original_text: str = Field(..., min_length=1)
    action: str = Field(..., pattern="^(rewrite|expand|custom)$")
    custom_instruction: Optional[str] = None


class ContentEditResponse(BaseModel):
    """AI 二改响应"""
    original_text: str
    edited_text: str


# ============= 聊天助手 =============

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1)
    history: Optional[List[ChatMessage]] = None
    context: Optional[str] = None  # 课程名称等上下文


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    role: str = "assistant"
