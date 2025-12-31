"""
作业提交 Service
"""
import base64
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
from app.services.minio_service import get_minio_service


class SubmissionService:
    """作业提交服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.submission_repo = SubmissionRepository(session)
        self.homework_repo = HomeworkRepository(session)
        self.student_repo = StudentRepository(session)
        self.course_repo = CourseRepository(session)
        self.minio = get_minio_service()

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
                        attachments=self._build_attachments_response(sub.attachments),
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

        # 上传新附件到 MinIO（使用 homework_id 作为文件夹）
        new_attachments_data = []
        if request.attachments:
            new_attachments_data = await self._upload_attachments(request.attachments, homework_id)

        # 保留的历史附件（转换为 dict 格式）
        existing_attachments_data = []
        if request.existing_attachments:
            existing_attachments_data = [
                {
                    "name": att.name,
                    "type": att.type,
                    "size": att.size,
                    "object_name": att.object_name
                }
                for att in request.existing_attachments
            ]

        # 合并附件列表：历史附件 + 新上传附件
        merged_attachments = existing_attachments_data + new_attachments_data
        attachments_data = merged_attachments if merged_attachments else None

        # 检查是否已有提交
        existing = await self.submission_repo.get_submission(homework_id, student.id)

        if existing:
            # 获取需要保留的 object_name 列表
            keep_object_names = {att.object_name for att in (request.existing_attachments or [])}

            # 只删除不再需要的旧附件
            if existing.attachments:
                for att in existing.attachments:
                    object_name = att.get("object_name")
                    if object_name and object_name not in keep_object_names:
                        try:
                            self.minio.delete_file(object_name)
                        except Exception:
                            pass

            # 更新现有提交（清除批改结果）
            update_data = {
                "content": request.content,
                "attachments": attachments_data,
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
                attachments=attachments_data
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
            # 删除旧附件
            if submission.attachments:
                for att in submission.attachments:
                    if att.get("object_name"):
                        try:
                            self.minio.delete_file(att["object_name"])
                        except Exception:
                            pass

            # 上传新附件（使用 homework_id 作为文件夹）
            update_data["attachments"] = await self._upload_attachments(request.attachments, submission.homework_id)

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

        # 删除附件
        if submission.attachments:
            for att in submission.attachments:
                if att.get("object_name"):
                    try:
                        self.minio.delete_file(att["object_name"])
                    except Exception:
                        pass

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
                        attachments=self._build_attachments_response(sub.attachments),
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

    async def _upload_attachments(self, attachments, homework_id: str) -> List[dict]:
        """上传附件列表到 MinIO

        Args:
            attachments: 附件列表
            homework_id: 作业 ID，用于将同一作业的提交文件组织在一个文件夹下
        """
        result = []
        for att in attachments:
            # 解码 Base64 内容
            content = att.content
            if "," in content:
                content = content.split(",", 1)[1]

            try:
                file_data = base64.b64decode(content)
            except Exception:
                raise ValueError(f"附件 {att.name} 的 Base64 编码无效")

            # 上传到 MinIO，使用 homework_id 作为文件夹
            object_name = self.minio.upload_file(
                file_data,
                att.name,
                att.type,
                prefix="submissions/",
                folder_id=homework_id
            )

            result.append({
                "name": att.name,
                "type": att.type,
                "size": att.size,
                "object_name": object_name
            })

        return result

    def _build_attachments_response(self, attachments: List[dict]) -> Optional[List[FileAttachment]]:
        """构建附件列表响应"""
        if not attachments:
            return None

        result = []
        for att in attachments:
            url = None
            if att.get("object_name"):
                url = self.minio.get_presigned_url(att["object_name"])

            result.append(FileAttachment(
                name=att.get("name", ""),
                type=att.get("type", ""),
                size=att.get("size", 0),
                object_name=att.get("object_name", ""),
                url=url
            ))

        return result

    def _to_response(self, submission: HomeworkSubmission) -> SubmissionResponse:
        """转换为响应对象"""
        return SubmissionResponse(
            id=submission.id,
            homework_id=submission.homework_id,
            student_id=submission.student_id,
            content=submission.content,
            attachments=self._build_attachments_response(submission.attachments),
            score=submission.score,
            feedback=submission.feedback,
            submitted_at=submission.submitted_at,
            graded_at=submission.graded_at
        )
