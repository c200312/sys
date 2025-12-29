"""
作业提交 Repository
"""
from typing import Optional, List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import HomeworkSubmission
from app.repositories.base import BaseRepository


class SubmissionRepository(BaseRepository[HomeworkSubmission]):
    """作业提交仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(HomeworkSubmission, session)

    async def get_by_homework_id(self, homework_id: str) -> List[HomeworkSubmission]:
        """获取作业的所有提交"""
        statement = select(HomeworkSubmission).where(
            HomeworkSubmission.homework_id == homework_id
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_student_id(self, student_id: str) -> List[HomeworkSubmission]:
        """获取学生的所有提交"""
        statement = select(HomeworkSubmission).where(
            HomeworkSubmission.student_id == student_id
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_submission(
        self, homework_id: str, student_id: str
    ) -> Optional[HomeworkSubmission]:
        """获取特定学生的特定作业提交"""
        statement = select(HomeworkSubmission).where(
            HomeworkSubmission.homework_id == homework_id,
            HomeworkSubmission.student_id == student_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def delete_by_homework_id(self, homework_id: str) -> int:
        """删除作业的所有提交"""
        submissions = await self.get_by_homework_id(homework_id)
        count = len(submissions)
        for submission in submissions:
            await self.session.delete(submission)
        await self.session.flush()
        return count

    async def delete_by_student_id(self, student_id: str) -> int:
        """删除学生的所有提交"""
        submissions = await self.get_by_student_id(student_id)
        count = len(submissions)
        for submission in submissions:
            await self.session.delete(submission)
        await self.session.flush()
        return count
