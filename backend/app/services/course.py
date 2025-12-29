"""
课程 Service
"""
from typing import Optional, List
from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.models import Course, CourseEnrollment, Student
from app.repositories import (
    CourseRepository,
    CourseEnrollmentRepository,
    StudentRepository,
    TeacherRepository,
    HomeworkRepository,
    SubmissionRepository,
    FolderRepository,
    FileRepository,
)
from app.schemas import (
    CourseCreateRequest,
    CourseUpdateRequest,
    CourseResponse,
    CourseListResponse,
    CourseWithTeacher,
    StudentCoursesResponse,
    TeacherCoursesResponse,
    StudentWithEnrollment,
    BatchAddResult,
)


class CourseService:
    """课程服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.course_repo = CourseRepository(session)
        self.enrollment_repo = CourseEnrollmentRepository(session)
        self.student_repo = StudentRepository(session)
        self.teacher_repo = TeacherRepository(session)
        self.homework_repo = HomeworkRepository(session)
        self.submission_repo = SubmissionRepository(session)
        self.folder_repo = FolderRepository(session)
        self.file_repo = FileRepository(session)

    async def get_courses(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> CourseListResponse:
        """获取课程列表"""
        courses, total = await self.course_repo.search(
            page=page,
            page_size=page_size,
            search=search
        )

        return CourseListResponse(
            courses=[
                CourseResponse(
                    id=c.id,
                    name=c.name,
                    description=c.description,
                    teacher_id=c.teacher_id,
                    student_count=c.student_count,
                    created_at=c.created_at
                ) for c in courses
            ],
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_course(self, course_id: str) -> CourseResponse:
        """获取单个课程"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        return CourseResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            teacher_id=course.teacher_id,
            student_count=course.student_count,
            created_at=course.created_at
        )

    async def create_course(
        self,
        request: CourseCreateRequest,
        teacher_id: str
    ) -> CourseResponse:
        """创建课程"""
        course = Course(
            name=request.name,
            description=request.description,
            teacher_id=teacher_id,
            student_count=0
        )
        course = await self.course_repo.create(course)

        return CourseResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            teacher_id=course.teacher_id,
            student_count=course.student_count,
            created_at=course.created_at
        )

    async def update_course(
        self,
        course_id: str,
        request: CourseUpdateRequest
    ) -> CourseResponse:
        """更新课程"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.description is not None:
            update_data["description"] = request.description

        if update_data:
            course = await self.course_repo.update(course, update_data)

        return CourseResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            teacher_id=course.teacher_id,
            student_count=course.student_count,
            created_at=course.created_at
        )

    async def delete_course(self, course_id: str) -> None:
        """删除课程（级联删除）"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        # 删除所有作业的提交记录
        homeworks = await self.homework_repo.get_by_course_id(course_id)
        for hw in homeworks:
            await self.submission_repo.delete_by_homework_id(hw.id)

        # 删除所有作业
        await self.homework_repo.delete_by_course_id(course_id)

        # 删除所有文件
        await self.file_repo.delete_by_course_id(course_id)

        # 删除所有文件夹
        await self.folder_repo.delete_by_course_id(course_id)

        # 删除所有选课记录
        await self.enrollment_repo.delete_by_course_id(course_id)

        # 删除课程
        await self.course_repo.delete(course)

    async def get_teacher_courses(self, teacher_id: str) -> TeacherCoursesResponse:
        """获取教师的课程列表"""
        courses = await self.course_repo.get_by_teacher_id(teacher_id)

        return TeacherCoursesResponse(
            courses=[
                CourseResponse(
                    id=c.id,
                    name=c.name,
                    description=c.description,
                    teacher_id=c.teacher_id,
                    student_count=c.student_count,
                    created_at=c.created_at
                ) for c in courses
            ],
            total=len(courses)
        )

    async def get_student_courses(self, student_id: str) -> StudentCoursesResponse:
        """
        获取学生的课程列表
        注意：student_id 实际上是 user_id（根据 /utils 实现）
        """
        enrollments = await self.enrollment_repo.get_by_student_id(student_id)

        courses_with_teacher = []
        for enrollment in enrollments:
            course = await self.course_repo.get_by_id(enrollment.course_id)
            if course:
                # 获取教师信息
                teacher = await self.teacher_repo.get_by_user_id(course.teacher_id)
                teacher_name = teacher.name if teacher else None

                courses_with_teacher.append(
                    CourseWithTeacher(
                        id=course.id,
                        name=course.name,
                        description=course.description,
                        teacher_id=course.teacher_id,
                        teacher_name=teacher_name,
                        student_count=course.student_count,
                        enrolled_at=enrollment.enrolled_at,
                        created_at=course.created_at
                    )
                )

        return StudentCoursesResponse(
            courses=courses_with_teacher,
            total=len(courses_with_teacher)
        )

    async def get_course_students(
        self,
        course_id: str,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> dict:
        """获取课程学员列表"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        enrollments = await self.enrollment_repo.get_by_course_id(course_id)

        # 获取所有学生信息
        students_with_enrollment = []
        for enrollment in enrollments:
            # enrollment.student_id 实际上是 user_id
            student = await self.student_repo.get_by_user_id(enrollment.student_id)
            if student:
                # 搜索过滤
                if search:
                    if search not in student.name and search not in student.student_no:
                        continue

                students_with_enrollment.append(
                    StudentWithEnrollment(
                        id=student.id,
                        student_no=student.student_no,
                        name=student.name,
                        class_name=student.class_name,
                        gender=student.gender.value,
                        created_at=student.created_at,
                        enrolled_at=enrollment.enrolled_at
                    )
                )

        # 按学号排序（提取数字部分进行数值排序）
        def extract_number(s):
            import re
            match = re.search(r'\d+', s.student_no)
            return int(match.group()) if match else 0

        students_with_enrollment.sort(key=extract_number)

        # 分页
        total = len(students_with_enrollment)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = students_with_enrollment[start:end]

        return {
            "students": paginated,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def add_student_to_course(
        self,
        course_id: str,
        student_id: str
    ) -> dict:
        """
        添加学员到课程
        注意：student_id 是 Student 表的 id，需要转换为 user_id
        """
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("学生不存在")

        # 使用 user_id 作为选课记录的 student_id
        if await self.enrollment_repo.is_enrolled(course_id, student.user_id):
            raise ConflictError("学生已在该课程中")

        enrollment = CourseEnrollment(
            course_id=course_id,
            student_id=student.user_id,
            enrolled_at=datetime.utcnow()
        )
        await self.enrollment_repo.create(enrollment)

        # 更新课程学生数
        await self.course_repo.update_student_count(course_id, 1)

        return {
            "message": "学员添加成功",
            "course_id": course_id,
            "student_id": student_id,
            "enrolled_at": enrollment.enrolled_at.isoformat()
        }

    async def batch_add_students(
        self,
        course_id: str,
        student_ids: List[str]
    ) -> BatchAddResult:
        """批量添加学员"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        added_count = 0
        failed_count = 0

        for student_id in student_ids:
            try:
                student = await self.student_repo.get_by_id(student_id)
                if not student:
                    failed_count += 1
                    continue

                if await self.enrollment_repo.is_enrolled(course_id, student.user_id):
                    failed_count += 1
                    continue

                enrollment = CourseEnrollment(
                    course_id=course_id,
                    student_id=student.user_id,
                    enrolled_at=datetime.utcnow()
                )
                await self.enrollment_repo.create(enrollment)
                added_count += 1
            except Exception:
                failed_count += 1

        # 更新课程学生数
        if added_count > 0:
            await self.course_repo.update_student_count(course_id, added_count)

        return BatchAddResult(
            added_count=added_count,
            failed_count=failed_count
        )

    async def remove_student_from_course(
        self,
        course_id: str,
        student_id: str
    ) -> None:
        """移除课程学员"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("学生不存在")

        if not await self.enrollment_repo.is_enrolled(course_id, student.user_id):
            raise NotFoundError("学生不在该课程中")

        await self.enrollment_repo.delete(course_id, student.user_id)

        # 更新课程学生数
        await self.course_repo.update_student_count(course_id, -1)
