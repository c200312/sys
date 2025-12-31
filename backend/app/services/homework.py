"""
作业 Service
"""
import base64
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
from app.services.minio_service import get_minio_service


class HomeworkService:
    """作业服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.homework_repo = HomeworkRepository(session)
        self.submission_repo = SubmissionRepository(session)
        self.course_repo = CourseRepository(session)
        self.student_repo = StudentRepository(session)
        self.minio = get_minio_service()

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

        # 处理附件上传
        attachment_data = None
        if request.attachment:
            attachment_data = await self._upload_attachment(request.attachment)

        # 处理批改标准文件上传
        grading_criteria_data = None
        if request.grading_criteria:
            grading_criteria_data = await self._process_grading_criteria(request.grading_criteria)

        homework = Homework(
            course_id=course_id,
            title=request.title,
            description=request.description,
            deadline=request.deadline,
            attachment=attachment_data,
            grading_criteria=grading_criteria_data
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

        # 处理附件更新
        if request.attachment is not None:
            # 删除旧附件
            if homework.attachment and homework.attachment.get("object_name"):
                try:
                    self.minio.delete_file(homework.attachment["object_name"])
                except Exception:
                    pass
            # 上传新附件
            update_data["attachment"] = await self._upload_attachment(request.attachment)

        # 处理批改标准更新
        if request.grading_criteria is not None:
            # 删除旧文件
            if homework.grading_criteria and homework.grading_criteria.get("object_name"):
                try:
                    self.minio.delete_file(homework.grading_criteria["object_name"])
                except Exception:
                    pass
            # 处理新批改标准
            update_data["grading_criteria"] = await self._process_grading_criteria(request.grading_criteria)

        if update_data:
            homework = await self.homework_repo.update(homework, update_data)

        return self._to_response(homework)

    async def delete_homework(self, homework_id: str) -> None:
        """删除作业（级联删除提交记录和附件）"""
        homework = await self.homework_repo.get_by_id(homework_id)
        if not homework:
            raise NotFoundError("作业不存在")

        # 删除附件
        if homework.attachment and homework.attachment.get("object_name"):
            try:
                self.minio.delete_file(homework.attachment["object_name"])
            except Exception:
                pass

        # 删除批改标准文件
        if homework.grading_criteria and homework.grading_criteria.get("object_name"):
            try:
                self.minio.delete_file(homework.grading_criteria["object_name"])
            except Exception:
                pass

        # 删除所有提交记录的附件
        submissions = await self.submission_repo.get_by_homework_id(homework_id)
        for sub in submissions:
            if sub.attachments:
                for att in sub.attachments:
                    if att.get("object_name"):
                        try:
                            self.minio.delete_file(att["object_name"])
                        except Exception:
                            pass

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
                    attachment=self._build_attachment_response(hw.attachment),
                    grading_criteria=self._build_grading_criteria_response(hw.grading_criteria),
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

    async def _upload_attachment(self, attachment) -> dict:
        """上传附件到 MinIO"""
        # 解码 Base64 内容
        content = attachment.content
        if "," in content:
            content = content.split(",", 1)[1]

        try:
            file_data = base64.b64decode(content)
        except Exception:
            raise ValueError("无效的 Base64 编码")

        # 上传到 MinIO
        object_name = self.minio.upload_file(
            file_data,
            attachment.name,
            attachment.type,
            prefix="homeworks/"
        )

        return {
            "name": attachment.name,
            "type": attachment.type,
            "size": attachment.size,
            "object_name": object_name
        }

    async def _process_grading_criteria(self, grading_criteria) -> dict:
        """处理批改标准"""
        if grading_criteria.type == "text":
            # 文本类型，直接存储
            return {
                "type": "text",
                "content": grading_criteria.content
            }
        else:
            # 文件类型，上传到 MinIO
            content = grading_criteria.content
            if "," in content:
                content = content.split(",", 1)[1]

            try:
                file_data = base64.b64decode(content)
            except Exception:
                raise ValueError("无效的 Base64 编码")

            object_name = self.minio.upload_file(
                file_data,
                grading_criteria.file_name or "grading_criteria",
                "application/octet-stream",
                prefix="homeworks/grading/"
            )

            return {
                "type": "file",
                "content": "",
                "file_name": grading_criteria.file_name,
                "file_size": grading_criteria.file_size,
                "object_name": object_name
            }

    def _build_attachment_response(self, attachment: dict) -> Optional[FileAttachment]:
        """构建附件响应对象"""
        if not attachment:
            return None

        url = None
        if attachment.get("object_name"):
            url = self.minio.get_presigned_url(attachment["object_name"])

        return FileAttachment(
            name=attachment.get("name", ""),
            type=attachment.get("type", ""),
            size=attachment.get("size", 0),
            object_name=attachment.get("object_name", ""),
            url=url
        )

    def _build_grading_criteria_response(self, grading_criteria: dict) -> Optional[GradingCriteria]:
        """构建批改标准响应对象"""
        if not grading_criteria:
            return None

        url = None
        if grading_criteria.get("object_name"):
            url = self.minio.get_presigned_url(grading_criteria["object_name"])

        return GradingCriteria(
            type=grading_criteria.get("type", "text"),
            content=grading_criteria.get("content", ""),
            file_name=grading_criteria.get("file_name"),
            file_size=grading_criteria.get("file_size"),
            object_name=grading_criteria.get("object_name"),
            url=url
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
            attachment=self._build_attachment_response(homework.attachment),
            grading_criteria=self._build_grading_criteria_response(homework.grading_criteria)
        )
