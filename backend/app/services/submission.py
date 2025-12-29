"""
作业提交 Service
"""
from typing import Optional, List
from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models import HomeworkSubmission
from app.repositories import (
    SubmissionRepository,
    HomeworkRepository,
    StudentRepository,
    CourseRepository,
)
from app.schemas import (
    SubmissionCreateRequest,
    SubmissionUpdateRequest,
    GradeRequest,
    SubmissionResponse,
    SubmissionWithStudent,
    SubmissionListResponse,
    GradeResponse,
    StudentSubmission,
    StudentSubmissionsResponse,
    FileAttachment,
)


class SubmissionService:
    """作业提交服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.submission_repo = SubmissionRepository(session)
        self.homework_repo = HomeworkRepository(session)
        self.student_repo = StudentRepository(session)
        self.course_repo = CourseRepository(session)

    async def get_homework_submissions(
        self,
        homework_id: str
    ) -> SubmissionListResponse:
        """获取作业提交列表"""
        homework = await self.homework_repo.get_by_id(homework_id)
        if not homework:
            raise NotFoundError("作业不存在")

        submissions = await self.submission_repo.get_by_homework_id(homework_id)

        result = []
        for sub in submissions:
            student = await self.student_repo.get_by_id(sub.student_id)
            if student:
                result.append(
                    SubmissionWithStudent(
                        id=sub.id,
                        homework_id=sub.homework_id,
                        student_id=sub.student_id,
                        student_name=student.name,
                        student_no=student.student_no,
                        student_class=student.class_name,
                        content=sub.content,
                        attachments=[FileAttachment(**a) for a in sub.attachments] if sub.attachments else None,
                        score=sub.score,
                        feedback=sub.feedback,
                        submitted_at=sub.submitted_at,
                        graded_at=sub.graded_at
                    )
                )

        return SubmissionListResponse(
            submissions=result,
            total=len(result)
        )

    async def get_submission(self, submission_id: str) -> SubmissionResponse:
        """获取单个提交"""
        submission = await self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise NotFoundError("提交不存在")

        return self._to_response(submission)

    async def create_submission(
        self,
        homework_id: str,
        student_id: str,
        request: SubmissionCreateRequest
    ) -> SubmissionResponse:
        """
        提交作业
        如果已有提交则更新（根据 /utils 实现）
        """
        homework = await self.homework_repo.get_by_id(homework_id)
        if not homework:
            raise NotFoundError("作业不存在")

        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("学生不存在")

        # 检查是否已有提交
        existing = await self.submission_repo.get_submission(homework_id, student.id)

        if existing:
            # 更新现有提交（清除批改结果）
            update_data = {
                "content": request.content,
                "attachments": [a.model_dump() for a in request.attachments] if request.attachments else None,
                "submitted_at": datetime.utcnow(),
                "score": None,
                "feedback": None,
                "graded_at": None
            }
            submission = await self.submission_repo.update(existing, update_data)
        else:
            # 创建新提交
            submission = HomeworkSubmission(
                homework_id=homework_id,
                student_id=student.id,
                content=request.content,
                attachments=[a.model_dump() for a in request.attachments] if request.attachments else None
            )
            submission = await self.submission_repo.create(submission)

        return self._to_response(submission)

    async def update_submission(
        self,
        submission_id: str,
        request: SubmissionUpdateRequest
    ) -> SubmissionResponse:
        """更新提交"""
        submission = await self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise NotFoundError("提交不存在")

        update_data = {}
        if request.content is not None:
            update_data["content"] = request.content
        if request.attachments is not None:
            update_data["attachments"] = [a.model_dump() for a in request.attachments]

        if update_data:
            update_data["submitted_at"] = datetime.utcnow()
            submission = await self.submission_repo.update(submission, update_data)

        return self._to_response(submission)

    async def grade_submission(
        self,
        submission_id: str,
        request: GradeRequest
    ) -> GradeResponse:
        """批改作业"""
        submission = await self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise NotFoundError("提交不存在")

        graded_at = datetime.utcnow()
        update_data = {
            "score": request.score,
            "feedback": request.feedback,
            "graded_at": graded_at
        }
        await self.submission_repo.update(submission, update_data)

        return GradeResponse(
            id=submission_id,
            score=request.score,
            feedback=request.feedback,
            graded_at=graded_at
        )

    async def delete_submission(self, submission_id: str) -> None:
        """删除提交"""
        submission = await self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise NotFoundError("提交不存在")

        await self.submission_repo.delete(submission)

    async def get_student_submissions(
        self,
        student_id: str
    ) -> StudentSubmissionsResponse:
        """获取学生的所有提交"""
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("学生不存在")

        submissions = await self.submission_repo.get_by_student_id(student.id)

        result = []
        for sub in submissions:
            homework = await self.homework_repo.get_by_id(sub.homework_id)
            if homework:
                course = await self.course_repo.get_by_id(homework.course_id)
                result.append(
                    StudentSubmission(
                        id=sub.id,
                        homework_id=sub.homework_id,
                        homework_title=homework.title,
                        course_name=course.name if course else "",
                        content=sub.content,
                        score=sub.score,
                        feedback=sub.feedback,
                        submitted_at=sub.submitted_at,
                        graded_at=sub.graded_at
                    )
                )

        return StudentSubmissionsResponse(
            submissions=result,
            total=len(result)
        )

    def _to_response(self, submission: HomeworkSubmission) -> SubmissionResponse:
        """转换为响应对象"""
        return SubmissionResponse(
            id=submission.id,
            homework_id=submission.homework_id,
            student_id=submission.student_id,
            content=submission.content,
            attachments=[FileAttachment(**a) for a in submission.attachments] if submission.attachments else None,
            score=submission.score,
            feedback=submission.feedback,
            submitted_at=submission.submitted_at,
            graded_at=submission.graded_at
        )
