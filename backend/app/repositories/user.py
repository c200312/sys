"""
用户 Repository
"""
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """用户仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_role(self, role: UserRole) -> list[User]:
        """根据角色获取用户列表"""
        statement = select(User).where(User.role == role)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def username_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        user = await self.get_by_username(username)
        return user is not None
