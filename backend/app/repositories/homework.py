"""
作业 Repository
"""
from typing import Optional, List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Homework
from app.repositories.base import BaseRepository


class HomeworkRepository(BaseRepository[Homework]):
    """作业仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(Homework, session)

    async def get_by_course_id(self, course_id: str) -> List[Homework]:
        """获取课程的所有作业"""
        statement = select(Homework).where(Homework.course_id == course_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def delete_by_course_id(self, course_id: str) -> int:
        """删除课程的所有作业"""
        homeworks = await self.get_by_course_id(course_id)
        count = len(homeworks)
        for homework in homeworks:
            await self.session.delete(homework)
        await self.session.flush()
        return count
