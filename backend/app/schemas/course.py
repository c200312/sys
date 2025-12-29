"""
课程相关 Schema
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ============= 请求 Schema =============

class CourseCreateRequest(BaseModel):
    """创建课程请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)


class CourseUpdateRequest(BaseModel):
    """更新课程请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)


class AddStudentRequest(BaseModel):
    """添加学员请求"""
    student_id: str = Field(..., min_length=1)


class BatchAddStudentsRequest(BaseModel):
    """批量添加学员请求"""
    student_ids: List[str] = Field(..., min_items=1)


# ============= 响应 Schema =============

class CourseResponse(BaseModel):
    """课程响应"""
    id: str
    name: str
    description: str
    teacher_id: str
    student_count: int
    created_at: datetime


class CourseListResponse(BaseModel):
    """课程列表响应"""
    courses: List[CourseResponse]
    total: int
    page: int
    page_size: int


class CourseWithTeacher(CourseResponse):
    """带教师信息的课程响应"""
    teacher_name: Optional[str] = None
    enrolled_at: Optional[datetime] = None


class StudentCoursesResponse(BaseModel):
    """学生课程列表响应"""
    courses: List[CourseWithTeacher]
    total: int


class TeacherCoursesResponse(BaseModel):
    """教师课程列表响应"""
    courses: List[CourseResponse]
    total: int


class BatchAddResult(BaseModel):
    """批量添加结果"""
    added_count: int
    failed_count: int
