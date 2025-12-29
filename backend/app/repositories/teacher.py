"""
教师 Repository
"""
from typing import Optional, List

from sqlmodel import select, or_
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Teacher
from app.repositories.base import BaseRepository


class TeacherRepository(BaseRepository[Teacher]):
    """教师仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(Teacher, session)

    async def get_by_user_id(self, user_id: str) -> Optional[Teacher]:
        """根据用户 ID 获取教师"""
        statement = select(Teacher).where(Teacher.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_teacher_no(self, teacher_no: str) -> Optional[Teacher]:
        """根据工号获取教师"""
        statement = select(Teacher).where(Teacher.teacher_no == teacher_no)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def teacher_no_exists(self, teacher_no: str) -> bool:
        """检查工号是否存在"""
        teacher = await self.get_by_teacher_no(teacher_no)
        return teacher is not None

    async def search(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> tuple[List[Teacher], int]:
        """搜索教师列表"""
        statement = select(Teacher)
        count_statement = select(Teacher)

        if search:
            search_filter = or_(
                Teacher.name.contains(search),
                Teacher.teacher_no.contains(search)
            )
            statement = statement.where(search_filter)
            count_statement = count_statement.where(search_filter)

        # 获取总数
        count_result = await self.session.execute(count_statement)
        total = len(list(count_result.scalars().all()))

        # 分页
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        result = await self.session.execute(statement)
        teachers = list(result.scalars().all())

        return teachers, total
