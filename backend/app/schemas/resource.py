"""
课程资源相关 Schema（文件夹和文件）
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ============= 请求 Schema =============

class FolderCreateRequest(BaseModel):
    """创建文件夹请求"""
    name: str = Field(..., min_length=1, max_length=200)


class FolderUpdateRequest(BaseModel):
    """更新文件夹请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)


class FileUploadRequest(BaseModel):
    """上传文件请求（用于 JSON 方式上传，已弃用）"""
    name: str = Field(..., min_length=1, max_length=255)
    size: int = Field(..., ge=0)
    type: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)  # Base64 编码（兼容旧接口）


class FileUpdateRequest(BaseModel):
    """更新文件请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)


# ============= 响应 Schema =============

class FileResponse(BaseModel):
    """文件响应"""
    id: str
    folder_id: str
    course_id: str
    name: str
    size: int
    type: str
    object_name: str  # MinIO 对象名称
    url: Optional[str] = None  # 下载 URL（预签名）
    created_at: datetime


class FileWithoutContent(BaseModel):
    """文件响应（不含内容，用于列表展示）"""
    id: str
    folder_id: str
    course_id: str
    name: str
    size: int
    type: str
    created_at: datetime


class FolderResponse(BaseModel):
    """文件夹响应"""
    id: str
    course_id: str
    name: str
    created_at: datetime


class FolderWithFiles(FolderResponse):
    """带文件列表的文件夹响应"""
    files: List[FileWithoutContent] = []


class FolderListResponse(BaseModel):
    """文件夹列表响应"""
    folders: List[FolderResponse]
    total: int


class FileListResponse(BaseModel):
    """文件列表响应"""
    files: List[FileResponse]
    total: int


class CourseResourcesResponse(BaseModel):
    """课程资源响应（文件夹带文件）
    注意：此结构来自 /utils 实现
    """
    folders: List[FolderWithFiles]
    total: int
