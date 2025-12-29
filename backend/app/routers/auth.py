"""
认证路由
实现 /api/auth/* 接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import DbSession, CurrentUserId
from app.core.exceptions import AppException
from app.services import AuthService
from app.schemas import (
    SignupRequest,
    LoginRequest,
    PasswordChangeRequest,
    UserResponse,
    LoginResponse,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/signup", status_code=status.HTTP_200_OK)
async def signup(request: SignupRequest, db: DbSession):
    """
    用户注册

    POST /api/auth/signup
    """
    try:
        service = AuthService(db)
        user = await service.signup(request)
        return {
            "success": True,
            "data": user.model_dump(),
            "message": "注册成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, db: DbSession):
    """
    用户登录

    POST /api/auth/login
    """
    try:
        service = AuthService(db)
        result = await service.login(request)
        return {
            "success": True,
            "data": result.model_dump(),
            "message": "登录成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(user_id: CurrentUserId):
    """
    用户登出

    POST /api/auth/logout
    """
    # Token 验证已在依赖中完成，这里直接返回成功
    # 实际项目中可以将 Token 加入黑名单
    return {
        "success": True,
        "message": "登出成功"
    }


@router.get("/verify", status_code=status.HTTP_200_OK)
async def verify_token(user_id: CurrentUserId, db: DbSession):
    """
    验证 Token

    GET /api/auth/verify
    """
    try:
        service = AuthService(db)
        user = await service.verify_token(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"success": False, "error": "Token无效或已过期", "code": "AUTH_002"}
            )
        return {
            "success": True,
            "data": user.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
