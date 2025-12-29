"""
AI 路由
实现 AI 相关接口

注意：这些接口目前使用 Mock Provider，逻辑仅供演示
真实 AI 集成需要替换 Provider 实现
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core import DbSession, CurrentUserId
from app.core.exceptions import AppException
from app.providers import get_ai_provider
from app.schemas import (
    PPTGenerateRequest,
    ContentGenerateRequest,
    ContentEditRequest,
    ChatRequest,
)

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/ppt/generate", status_code=status.HTTP_200_OK)
async def generate_ppt(
    request: PPTGenerateRequest,
    user_id: CurrentUserId
):
    """
    生成 PPT

    POST /api/ai/ppt/generate

    ai/ppt: PPT 生成接口
    """
    try:
        provider = get_ai_provider()
        result = await provider.generate_ppt(request)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "error": str(e), "code": "AI_001"}
        )


@router.post("/content/generate", status_code=status.HTTP_200_OK)
async def generate_content(
    request: ContentGenerateRequest,
    user_id: CurrentUserId
):
    """
    生成教学资源

    POST /api/ai/content/generate

    ai/content: 教学资源生成接口
    """
    try:
        provider = get_ai_provider()
        result = await provider.generate_content(request)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "error": str(e), "code": "AI_001"}
        )


@router.post("/content/edit", status_code=status.HTTP_200_OK)
async def edit_content(
    request: ContentEditRequest,
    user_id: CurrentUserId
):
    """
    AI 二改

    POST /api/ai/content/edit

    ai/edit: 内容修改接口
    """
    try:
        provider = get_ai_provider()
        result = await provider.edit_content(request)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "error": str(e), "code": "AI_001"}
        )


@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    user_id: CurrentUserId
):
    """
    AI 聊天

    POST /api/ai/chat

    ai/chat: 聊天助手接口
    """
    try:
        provider = get_ai_provider()
        result = await provider.chat(request)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "error": str(e), "code": "AI_001"}
        )
