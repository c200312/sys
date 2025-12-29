"""
课程 Repository
"""
from typing import Optional, List

from sqlmodel import select, or_
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Course, CourseEnrollment
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    """课程仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_teacher_id(self, teacher_id: str) -> List[Course]:
        """获取教师的课程列表"""
        statement = select(Course).where(Course.teacher_id == teacher_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def search(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> tuple[List[Course], int]:
        """搜索课程列表"""
        statement = select(Course)
        count_statement = select(Course)

        if search:
            statement = statement.where(Course.name.contains(search))
            count_statement = count_statement.where(Course.name.contains(search))

        # 获取总数
        count_result = await self.session.execute(count_statement)
        total = len(list(count_result.scalars().all()))

        # 分页
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        result = await self.session.execute(statement)
        courses = list(result.scalars().all())

        return courses, total

    async def update_student_count(self, course_id: str, delta: int) -> None:
        """更新学生数量"""
        course = await self.get_by_id(course_id)
        if course:
            course.student_count = max(0, course.student_count + delta)
            self.session.add(course)
            await self.session.flush()


class CourseEnrollmentRepository:
    """课程选课仓库"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_course_id(self, course_id: str) -> List[CourseEnrollment]:
        """获取课程的所有选课记录"""
        statement = select(CourseEnrollment).where(
            CourseEnrollment.course_id == course_id
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_student_id(self, student_id: str) -> List[CourseEnrollment]:
        """获取学生的所有选课记录"""
        statement = select(CourseEnrollment).where(
            CourseEnrollment.student_id == student_id
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_enrollment(
        self, course_id: str, student_id: str
    ) -> Optional[CourseEnrollment]:
        """获取特定的选课记录"""
        statement = select(CourseEnrollment).where(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.student_id == student_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def is_enrolled(self, course_id: str, student_id: str) -> bool:
        """检查学生是否已选课"""
        enrollment = await self.get_enrollment(course_id, student_id)
        return enrollment is not None

    async def create(self, enrollment: CourseEnrollment) -> CourseEnrollment:
        """创建选课记录"""
        self.session.add(enrollment)
        await self.session.flush()
        return enrollment

    async def delete(self, course_id: str, student_id: str) -> bool:
        """删除选课记录"""
        enrollment = await self.get_enrollment(course_id, student_id)
        if enrollment:
            await self.session.delete(enrollment)
            await self.session.flush()
            return True
        return False

    async def delete_by_course_id(self, course_id: str) -> int:
        """删除课程的所有选课记录"""
        enrollments = await self.get_by_course_id(course_id)
        count = len(enrollments)
        for enrollment in enrollments:
            await self.session.delete(enrollment)
        await self.session.flush()
        return count

    async def delete_by_student_id(self, student_id: str) -> int:
        """删除学生的所有选课记录"""
        enrollments = await self.get_by_student_id(student_id)
        count = len(enrollments)
        for enrollment in enrollments:
            await self.session.delete(enrollment)
        await self.session.flush()
        return count

    async def has_enrollments(self, student_id: str) -> bool:
        """检查学生是否有选课记录"""
        enrollments = await self.get_by_student_id(student_id)
        return len(enrollments) > 0
