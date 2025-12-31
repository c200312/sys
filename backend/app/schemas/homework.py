"""
作业相关 Schema
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ============= 嵌套类型 =============

class FileAttachment(BaseModel):
    """文件附件（用于响应）"""
    name: str
    type: str  # MIME 类型
    size: int  # 字节
    object_name: str  # MinIO 对象名称
    url: Optional[str] = None  # 下载 URL（预签名）


class FileAttachmentUpload(BaseModel):
    """文件附件上传请求（Base64 方式）"""
    name: str
    type: str  # MIME 类型
    size: int  # 字节
    content: str  # Base64 编码


class ExistingAttachment(BaseModel):
    """已存在的附件（重新提交时保留）"""
    name: str
    type: str
    size: int
    object_name: str  # MinIO 对象名称


class GradingCriteria(BaseModel):
    """批改标准"""
    type: str = Field(..., pattern="^(text|file)$")
    content: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    object_name: Optional[str] = None  # MinIO 对象名称（type=file 时）
    url: Optional[str] = None  # 下载 URL（预签名）


class GradingCriteriaUpload(BaseModel):
    """批改标准上传请求"""
    type: str = Field(..., pattern="^(text|file)$")
    content: str  # 文本内容或 Base64 编码的文件
    file_name: Optional[str] = None
    file_size: Optional[int] = None


# ============= 请求 Schema =============

class HomeworkCreateRequest(BaseModel):
    """创建作业请求"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    deadline: datetime
    attachment: Optional[FileAttachmentUpload] = None
    grading_criteria: Optional[GradingCriteriaUpload] = None


class HomeworkUpdateRequest(BaseModel):
    """更新作业请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    attachment: Optional[FileAttachmentUpload] = None
    grading_criteria: Optional[GradingCriteriaUpload] = None


# ============= 响应 Schema =============

class HomeworkResponse(BaseModel):
    """作业响应"""
    id: str
    course_id: str
    title: str
    description: str
    deadline: datetime
    created_at: datetime
    attachment: Optional[FileAttachment] = None
    grading_criteria: Optional[GradingCriteria] = None


class HomeworkListResponse(BaseModel):
    """作业列表响应"""
    homeworks: List[HomeworkResponse]
    total: int


class StudentHomework(HomeworkResponse):
    """学生视角的作业（含提交状态）
    注意：此 Schema 基于 /utils 实现，docs 未明确定义
    """
    status: str  # pending | submitted | graded
    submission_id: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None


class StudentHomeworksResponse(BaseModel):
    """学生作业列表响应"""
    homeworks: List[StudentHomework]
    total: int
