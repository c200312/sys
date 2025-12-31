"""
作业提交相关 Schema
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator

from app.schemas.homework import FileAttachment, FileAttachmentUpload, ExistingAttachment


# ============= 请求 Schema =============

class SubmissionCreateRequest(BaseModel):
    """提交作业请求（文本或附件至少有一个）"""
    content: Optional[str] = None
    attachments: Optional[List[FileAttachmentUpload]] = None  # 新上传的附件
    existing_attachments: Optional[List[ExistingAttachment]] = None  # 保留的历史附件

    @model_validator(mode='after')
    def check_content_or_attachments(self):
        """验证文本或附件至少有一个"""
        has_content = self.content and self.content.strip()
        has_new_attachments = self.attachments and len(self.attachments) > 0
        has_existing_attachments = self.existing_attachments and len(self.existing_attachments) > 0
        if not has_content and not has_new_attachments and not has_existing_attachments:
            raise ValueError('请填写作业内容或上传附件')
        return self


class SubmissionUpdateRequest(BaseModel):
    """更新提交请求"""
    content: Optional[str] = None
    attachments: Optional[List[FileAttachmentUpload]] = None


class GradeRequest(BaseModel):
    """批改请求"""
    score: int = Field(..., ge=0, le=100)
    feedback: Optional[str] = None


# ============= 响应 Schema =============

class SubmissionResponse(BaseModel):
    """提交响应"""
    id: str
    homework_id: str
    student_id: str
    content: Optional[str] = None
    attachments: Optional[List[FileAttachment]] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None


class SubmissionWithStudent(SubmissionResponse):
    """带学生信息的提交响应"""
    student_name: str
    student_no: str
    student_class: str


class SubmissionListResponse(BaseModel):
    """提交列表响应"""
    submissions: List[SubmissionWithStudent]
    total: int


class GradeResponse(BaseModel):
    """批改响应"""
    id: str
    score: int
    feedback: Optional[str]
    graded_at: datetime


class StudentSubmission(BaseModel):
    """学生提交记录（含作业信息）"""
    id: str
    homework_id: str
    homework_title: str
    course_name: str
    content: Optional[str] = None
    attachments: Optional[List[FileAttachment]] = None  # 附件列表
    score: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None


class StudentSubmissionsResponse(BaseModel):
    """学生提交列表响应"""
    submissions: List[StudentSubmission]
    total: int
