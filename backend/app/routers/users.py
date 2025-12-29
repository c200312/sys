"""
用户路由
实现 /api/users/* 接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import DbSession, CurrentUserId
from app.core.exceptions import AppException
from app.services import AuthService
from app.schemas import PasswordChangeRequest

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(user_id: CurrentUserId, db: DbSession):
    """
    获取当前用户信息

    GET /api/users/me
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


@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
    request: PasswordChangeRequest,
    user_id: CurrentUserId,
    db: DbSession
):
    """
    修改密码

    PUT /api/users/password
    """
    try:
        service = AuthService(db)
        await service.change_password(
            user_id=user_id,
            old_password=request.old_password,
            new_password=request.new_password
        )
        return {
            "success": True,
            "message": "密码修改成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
