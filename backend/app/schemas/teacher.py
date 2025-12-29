"""
教师相关 Schema
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ============= 请求 Schema =============

class TeacherCreateRequest(BaseModel):
    """创建教师请求"""
    teacher_no: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    gender: str = Field(..., pattern="^(男|女)$")
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1)


class TeacherUpdateRequest(BaseModel):
    """更新教师请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    gender: Optional[str] = Field(None, pattern="^(男|女)$")
    email: Optional[str] = Field(None, max_length=255)


# ============= 响应 Schema =============

class TeacherResponse(BaseModel):
    """教师响应"""
    id: str
    teacher_no: str
    name: str
    gender: str
    email: str
    created_at: datetime


class TeacherListResponse(BaseModel):
    """教师列表响应"""
    teachers: List[TeacherResponse]
    total: int
    page: int
    page_size: int
