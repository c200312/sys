"""
认证 Service
"""
from datetime import timedelta
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import (
    get_settings,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.core.exceptions import (
    AuthenticationError,
    UserExistsError,
    ValidationError,
)
from app.models import User, UserRole
from app.repositories import UserRepository
from app.schemas import (
    SignupRequest,
    LoginRequest,
    LoginResponse,
    UserBase,
    UserResponse,
)

settings = get_settings()


class AuthService:
    """认证服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def signup(self, request: SignupRequest) -> UserResponse:
        """
        用户注册

        Args:
            request: 注册请求

        Returns:
            创建的用户信息

        Raises:
            UserExistsError: 用户名已存在
        """
        # 检查用户名是否存在
        if await self.user_repo.username_exists(request.username):
            raise UserExistsError("用户名已存在")

        # 创建用户
        user = User(
            username=request.username,
            password=get_password_hash(request.password),
            role=UserRole(request.role)
        )
        user = await self.user_repo.create(user)

        return UserResponse(
            id=user.id,
            username=user.username,
            role=user.role.value,
            created_at=user.created_at
        )

    async def login(self, request: LoginRequest) -> LoginResponse:
        """
        用户登录

        Args:
            request: 登录请求

        Returns:
            Token 和用户信息

        Raises:
            AuthenticationError: 用户名或密码错误
        """
        # 查找用户
        user = await self.user_repo.get_by_username(request.username)
        if not user:
            raise AuthenticationError("用户名或密码错误")

        # 验证密码
        if not verify_password(request.password, user.password):
            raise AuthenticationError("用户名或密码错误")

        # 生成 Token
        token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value
        }
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )

        return LoginResponse(
            access_token=access_token,
            token_type="Bearer",
            user=UserBase(
                id=user.id,
                username=user.username,
                role=user.role.value
            )
        )

    async def verify_token(self, user_id: str) -> Optional[UserResponse]:
        """
        验证 Token 并获取用户信息

        Args:
            user_id: 用户 ID（从 Token 解析）

        Returns:
            用户信息
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        return UserResponse(
            id=user.id,
            username=user.username,
            role=user.role.value,
            created_at=user.created_at
        )

    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        修改密码

        Args:
            user_id: 用户 ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            是否成功

        Raises:
            ValidationError: 旧密码错误
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValidationError("用户不存在", "VALID_003")

        # 验证旧密码
        if not verify_password(old_password, user.password):
            raise ValidationError("旧密码错误", "VALID_003")

        # 更新密码
        await self.user_repo.update(user, {
            "password": get_password_hash(new_password)
        })

        return True
