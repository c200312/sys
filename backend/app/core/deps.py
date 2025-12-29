"""
依赖注入模块
FastAPI 依赖项
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import TokenError
from app.core.security import decode_access_token
from app.db.session import get_session

# HTTP Bearer Token 安全方案
security = HTTPBearer()


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async for session in get_session():
        yield session


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """
    从 Token 中获取当前用户 ID

    Raises:
        HTTPException: 如果 Token 无效
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": "Token无效或已过期", "code": "AUTH_002"}
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": "Token无效或已过期", "code": "AUTH_002"}
        )

    return user_id


async def get_current_user_info(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> dict:
    """
    从 Token 中获取当前用户完整信息

    Returns:
        包含 id, username, role 的字典
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": "Token无效或已过期", "code": "AUTH_002"}
        )

    return {
        "id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role")
    }


# 类型别名
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUserInfo = Annotated[dict, Depends(get_current_user_info)]
