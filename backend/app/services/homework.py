"""
作业 Service
"""
from typing import Optional, List
from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Homework
from app.repositories import (
    HomeworkRepository,
    SubmissionRepository,
    CourseRepository,
    StudentRepository,
)
from app.schemas import (
    HomeworkCreateRequest,
    HomeworkUpdateRequest,
    HomeworkResponse,
    HomeworkListResponse,
    FileAttachment,
    GradingCriteria,
    StudentHomework,
    StudentHomeworksResponse,
)


class HomeworkService:
    """作业服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.homework_repo = HomeworkRepository(session)
        self.submission_repo = SubmissionRepository(session)
        self.course_repo = CourseRepository(session)
        self.student_repo = StudentRepository(session)

    async def get_course_homeworks(self, course_id: str) -> HomeworkListResponse:
        """获取课程作业列表"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        homeworks = await self.homework_repo.get_by_course_id(course_id)

        return HomeworkListResponse(
            homeworks=[
                self._to_response(hw) for hw in homeworks
            ],
            total=len(homeworks)
        )

    async def get_homework(self, homework_id: str) -> HomeworkResponse:
        """获取单个作业"""
        homework = await self.homework_repo.get_by_id(homework_id)
        if not homework:
            raise NotFoundError("作业不存在")

        return self._to_response(homework)

    async def create_homework(
        self,
        course_id: str,
        request: HomeworkCreateRequest
    ) -> HomeworkResponse:
        """创建作业"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        homework = Homework(
            course_id=course_id,
            title=request.title,
            description=request.description,
            deadline=request.deadline,
            attachment=request.attachment.model_dump() if request.attachment else None,
            grading_criteria=request.grading_criteria.model_dump() if request.grading_criteria else None
        )
        homework = await self.homework_repo.create(homework)

        return self._to_response(homework)

    async def update_homework(
        self,
        homework_id: str,
        request: HomeworkUpdateRequest
    ) -> HomeworkResponse:
        """更新作业"""
        homework = await self.homework_repo.get_by_id(homework_id)
        if not homework:
            raise NotFoundError("作业不存在")

        update_data = {}
        if request.title is not None:
            update_data["title"] = request.title
        if request.description is not None:
            update_data["description"] = request.description
        if request.deadline is not None:
            update_data["deadline"] = request.deadline
        if request.attachment is not None:
            update_data["attachment"] = request.attachment.model_dump()
        if request.grading_criteria is not None:
            update_data["grading_criteria"] = request.grading_criteria.model_dump()

        if update_data:
            homework = await self.homework_repo.update(homework, update_data)

        return self._to_response(homework)

    async def delete_homework(self, homework_id: str) -> None:
        """删除作业（级联删除提交记录）"""
        homework = await self.homework_repo.get_by_id(homework_id)
        if not homework:
            raise NotFoundError("作业不存在")

        # 删除所有提交记录
        await self.submission_repo.delete_by_homework_id(homework_id)

        # 删除作业
        await self.homework_repo.delete(homework)

    async def get_student_homeworks(
        self,
        student_id: str,
        course_id: str
    ) -> StudentHomeworksResponse:
        """
        获取学生课程作业列表（含提交状态）
        注意：此接口基于 /utils 实现，docs 未明确定义
        """
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        # 获取学生信息
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("学生不存在")

        homeworks = await self.homework_repo.get_by_course_id(course_id)

        result = []
        for hw in homeworks:
            # 查找该学生的提交记录
            submission = await self.submission_repo.get_submission(hw.id, student.id)

            # 计算状态
            if submission:
                if submission.score is not None:
                    status = "graded"
                else:
                    status = "submitted"
            else:
                status = "pending"

            result.append(
                StudentHomework(
                    id=hw.id,
                    course_id=hw.course_id,
                    title=hw.title,
                    description=hw.description,
                    deadline=hw.deadline,
                    created_at=hw.created_at,
                    attachment=FileAttachment(**hw.attachment) if hw.attachment else None,
                    grading_criteria=GradingCriteria(**hw.grading_criteria) if hw.grading_criteria else None,
                    status=status,
                    submission_id=submission.id if submission else None,
                    score=submission.score if submission else None,
                    feedback=submission.feedback if submission else None
                )
            )

        return StudentHomeworksResponse(
            homeworks=result,
            total=len(result)
        )

    def _to_response(self, homework: Homework) -> HomeworkResponse:
        """转换为响应对象"""
        return HomeworkResponse(
            id=homework.id,
            course_id=homework.course_id,
            title=homework.title,
            description=homework.description,
            deadline=homework.deadline,
            created_at=homework.created_at,
            attachment=FileAttachment(**homework.attachment) if homework.attachment else None,
            grading_criteria=GradingCriteria(**homework.grading_criteria) if homework.grading_criteria else None
        )
