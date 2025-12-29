"""
学生 Service
"""
from typing import Optional, List

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import get_password_hash
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.models import User, UserRole, Student, Gender
from app.repositories import (
    UserRepository,
    StudentRepository,
    CourseEnrollmentRepository,
    SubmissionRepository,
)
from app.schemas import (
    StudentCreateRequest,
    StudentUpdateRequest,
    StudentResponse,
    StudentListResponse,
)


class StudentService:
    """学生服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.student_repo = StudentRepository(session)
        self.enrollment_repo = CourseEnrollmentRepository(session)
        self.submission_repo = SubmissionRepository(session)

    async def get_students(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        class_filter: Optional[str] = None
    ) -> StudentListResponse:
        """获取学生列表"""
        students, total = await self.student_repo.search(
            page=page,
            page_size=page_size,
            search=search,
            class_filter=class_filter
        )

        return StudentListResponse(
            students=[
                StudentResponse(
                    id=s.id,
                    student_no=s.student_no,
                    name=s.name,
                    class_name=s.class_name,
                    gender=s.gender.value,
                    created_at=s.created_at
                ) for s in students
            ],
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_student(self, student_id: str) -> StudentResponse:
        """获取单个学生"""
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("学生不存在")

        return StudentResponse(
            id=student.id,
            student_no=student.student_no,
            name=student.name,
            class_name=student.class_name,
            gender=student.gender.value,
            created_at=student.created_at
        )

    async def get_student_by_user_id(self, user_id: str) -> StudentResponse:
        """根据用户 ID 获取学生"""
        student = await self.student_repo.get_by_user_id(user_id)
        if not student:
            raise NotFoundError("学生不存在")

        return StudentResponse(
            id=student.id,
            student_no=student.student_no,
            name=student.name,
            class_name=student.class_name,
            gender=student.gender.value,
            created_at=student.created_at
        )

    async def get_class_list(self) -> List[str]:
        """获取班级列表"""
        return await self.student_repo.get_class_list()

    async def create_student(self, request: StudentCreateRequest) -> StudentResponse:
        """创建学生"""
        # 检查学号是否存在
        if await self.student_repo.student_no_exists(request.student_no):
            raise ConflictError("学号已存在", "RES_003")

        # 检查用户名是否存在
        if await self.user_repo.username_exists(request.student_no):
            raise ConflictError("用户名已存在", "AUTH_003")

        # 创建用户账号
        user = User(
            username=request.student_no,
            password=get_password_hash(request.password),
            role=UserRole.STUDENT
        )
        user = await self.user_repo.create(user)

        # 创建学生详情
        student = Student(
            user_id=user.id,
            student_no=request.student_no,
            name=request.name,
            class_name=request.class_name,
            gender=Gender(request.gender)
        )
        student = await self.student_repo.create(student)

        return StudentResponse(
            id=student.id,
            student_no=student.student_no,
            name=student.name,
            class_name=student.class_name,
            gender=student.gender.value,
            created_at=student.created_at
        )

    async def update_student(
        self,
        student_id: str,
        request: StudentUpdateRequest
    ) -> StudentResponse:
        """更新学生"""
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("学生不存在")

        # 更新字段
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.class_name is not None:
            update_data["class_name"] = request.class_name
        if request.gender is not None:
            update_data["gender"] = Gender(request.gender)

        if update_data:
            student = await self.student_repo.update(student, update_data)

        return StudentResponse(
            id=student.id,
            student_no=student.student_no,
            name=student.name,
            class_name=student.class_name,
            gender=student.gender.value,
            created_at=student.created_at
        )

    async def delete_student(self, student_id: str) -> None:
        """删除学生"""
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("学生不存在")

        # 检查是否有选课记录（根据 /utils 实现）
        # 注意：使用 user_id 作为 student_id 来检查选课
        if await self.enrollment_repo.has_enrollments(student.user_id):
            raise ValidationError("该学生已有选课记录，无法删除", "VALID_003")

        # 删除学生的所有提交记录
        await self.submission_repo.delete_by_student_id(student.id)

        # 删除用户账号
        await self.user_repo.delete_by_id(student.user_id)

        # 删除学生详情
        await self.student_repo.delete(student)
