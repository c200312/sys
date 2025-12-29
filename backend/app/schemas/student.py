"""
学生相关 Schema
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ============= 请求 Schema =============

class StudentCreateRequest(BaseModel):
    """创建学生请求"""
    student_no: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    # 注意：docs 中用的是 "class"，但 Python 关键字冲突，API 层会转换
    class_name: str = Field(..., min_length=1, max_length=50, alias="class")
    gender: str = Field(..., pattern="^(男|女)$")
    password: str = Field(..., min_length=1)

    class Config:
        populate_by_name = True


class StudentUpdateRequest(BaseModel):
    """更新学生请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    class_name: Optional[str] = Field(None, min_length=1, max_length=50, alias="class")
    gender: Optional[str] = Field(None, pattern="^(男|女)$")

    class Config:
        populate_by_name = True


# ============= 响应 Schema =============

class StudentResponse(BaseModel):
    """学生响应"""
    id: str
    student_no: str
    name: str
    # 输出时使用 "class" 作为字段名，符合 docs 规范
    class_name: str = Field(..., serialization_alias="class")
    gender: str
    created_at: datetime

    class Config:
        populate_by_name = True


class StudentListResponse(BaseModel):
    """学生列表响应"""
    students: List[StudentResponse]
    total: int
    page: int
    page_size: int


class StudentWithEnrollment(StudentResponse):
    """带选课时间的学生响应"""
    enrolled_at: datetime
