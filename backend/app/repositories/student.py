"""
学生 Repository
"""
from typing import Optional, List

from sqlmodel import select, or_, distinct, func, cast, Integer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    """学生仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(Student, session)

    async def get_by_user_id(self, user_id: str) -> Optional[Student]:
        """根据用户 ID 获取学生"""
        statement = select(Student).where(Student.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_student_no(self, student_no: str) -> Optional[Student]:
        """根据学号获取学生"""
        statement = select(Student).where(Student.student_no == student_no)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def student_no_exists(self, student_no: str) -> bool:
        """检查学号是否存在"""
        student = await self.get_by_student_no(student_no)
        return student is not None

    async def search(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        class_filter: Optional[str] = None
    ) -> tuple[List[Student], int]:
        """搜索学生列表"""
        statement = select(Student)

        # 搜索过滤
        if search:
            search_filter = or_(
                Student.name.contains(search),
                Student.student_no.contains(search)
            )
            statement = statement.where(search_filter)

        # 班级过滤
        if class_filter:
            statement = statement.where(Student.class_name == class_filter)

        # 获取所有匹配的学生
        result = await self.session.execute(statement)
        all_students = list(result.scalars().all())

        # 内存中按学号数字排序
        import re
        def extract_number(s):
            match = re.search(r'\d+', s.student_no)
            return int(match.group()) if match else 0
        all_students.sort(key=extract_number)

        # 获取总数
        total = len(all_students)

        # 分页
        offset = (page - 1) * page_size
        students = all_students[offset:offset + page_size]

        return students, total

    async def get_class_list(self) -> List[str]:
        """获取所有班级列表（去重）"""
        statement = select(distinct(Student.class_name))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_ids(self, ids: List[str]) -> List[Student]:
        """根据 ID 列表获取学生"""
        if not ids:
            return []
        statement = select(Student).where(Student.id.in_(ids))
        result = await self.session.execute(statement)
        return list(result.scalars().all())
