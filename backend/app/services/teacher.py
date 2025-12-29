"""
教师 Service
"""
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import get_password_hash
from app.core.exceptions import NotFoundError, ConflictError
from app.models import User, UserRole, Teacher, Gender
from app.repositories import UserRepository, TeacherRepository
from app.schemas import (
    TeacherCreateRequest,
    TeacherUpdateRequest,
    TeacherResponse,
    TeacherListResponse,
)


class TeacherService:
    """教师服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.teacher_repo = TeacherRepository(session)

    async def get_teachers(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> TeacherListResponse:
        """获取教师列表"""
        teachers, total = await self.teacher_repo.search(
            page=page,
            page_size=page_size,
            search=search
        )

        return TeacherListResponse(
            teachers=[
                TeacherResponse(
                    id=t.id,
                    teacher_no=t.teacher_no,
                    name=t.name,
                    gender=t.gender.value,
                    email=t.email,
                    created_at=t.created_at
                ) for t in teachers
            ],
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_teacher(self, teacher_id: str) -> TeacherResponse:
        """获取单个教师"""
        teacher = await self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise NotFoundError("教师不存在")

        return TeacherResponse(
            id=teacher.id,
            teacher_no=teacher.teacher_no,
            name=teacher.name,
            gender=teacher.gender.value,
            email=teacher.email,
            created_at=teacher.created_at
        )

    async def get_teacher_by_user_id(self, user_id: str) -> TeacherResponse:
        """根据用户 ID 获取教师"""
        teacher = await self.teacher_repo.get_by_user_id(user_id)
        if not teacher:
            raise NotFoundError("教师不存在")

        return TeacherResponse(
            id=teacher.id,
            teacher_no=teacher.teacher_no,
            name=teacher.name,
            gender=teacher.gender.value,
            email=teacher.email,
            created_at=teacher.created_at
        )

    async def create_teacher(self, request: TeacherCreateRequest) -> TeacherResponse:
        """创建教师"""
        # 检查工号是否存在
        if await self.teacher_repo.teacher_no_exists(request.teacher_no):
            raise ConflictError("教师工号已存在", "RES_003")

        # 检查用户名是否存在
        if await self.user_repo.username_exists(request.teacher_no):
            raise ConflictError("用户名已存在", "AUTH_003")

        # 创建用户账号
        user = User(
            username=request.teacher_no,
            password=get_password_hash(request.password),
            role=UserRole.TEACHER
        )
        user = await self.user_repo.create(user)

        # 创建教师详情
        teacher = Teacher(
            user_id=user.id,
            teacher_no=request.teacher_no,
            name=request.name,
            gender=Gender(request.gender),
            email=request.email
        )
        teacher = await self.teacher_repo.create(teacher)

        return TeacherResponse(
            id=teacher.id,
            teacher_no=teacher.teacher_no,
            name=teacher.name,
            gender=teacher.gender.value,
            email=teacher.email,
            created_at=teacher.created_at
        )

    async def update_teacher(
        self,
        teacher_id: str,
        request: TeacherUpdateRequest
    ) -> TeacherResponse:
        """更新教师"""
        teacher = await self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise NotFoundError("教师不存在")

        # 更新字段
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.gender is not None:
            update_data["gender"] = Gender(request.gender)
        if request.email is not None:
            update_data["email"] = request.email

        if update_data:
            teacher = await self.teacher_repo.update(teacher, update_data)

        return TeacherResponse(
            id=teacher.id,
            teacher_no=teacher.teacher_no,
            name=teacher.name,
            gender=teacher.gender.value,
            email=teacher.email,
            created_at=teacher.created_at
        )

    async def delete_teacher(self, teacher_id: str) -> None:
        """删除教师"""
        teacher = await self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise NotFoundError("教师不存在")

        # 删除用户账号
        await self.user_repo.delete_by_id(teacher.user_id)

        # 删除教师详情
        await self.teacher_repo.delete(teacher)
