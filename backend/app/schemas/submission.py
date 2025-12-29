"""
作业提交相关 Schema
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.schemas.homework import FileAttachment


# ============= 请求 Schema =============

class SubmissionCreateRequest(BaseModel):
    """提交作业请求"""
    content: str = Field(..., min_length=1)
    attachments: Optional[List[FileAttachment]] = None


class SubmissionUpdateRequest(BaseModel):
    """更新提交请求"""
    content: Optional[str] = None
    attachments: Optional[List[FileAttachment]] = None


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
    content: str
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
    content: str
    score: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None


class StudentSubmissionsResponse(BaseModel):
    """学生提交列表响应"""
    submissions: List[StudentSubmission]
    total: int
