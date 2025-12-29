"""
数据库模型定义
使用 SQLModel 定义所有实体
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, JSON


# ============= 枚举类型 =============

class UserRole(str, Enum):
    """用户角色"""
    TEACHER = "teacher"
    STUDENT = "student"


class Gender(str, Enum):
    """性别"""
    MALE = "男"
    FEMALE = "女"


class GradingCriteriaType(str, Enum):
    """批改标准类型"""
    TEXT = "text"
    FILE = "file"


# ============= 关联表 =============

class CourseEnrollment(SQLModel, table=True):
    """
    课程选课记录表 (多对多关联)
    关联 Course 和 Student
    """
    __tablename__ = "course_enrollments"

    course_id: str = Field(foreign_key="courses.id", primary_key=True)
    student_id: str = Field(foreign_key="users.id", primary_key=True)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)


# ============= 核心实体 =============

class User(SQLModel, table=True):
    """
    用户表
    存储所有用户的登录信息
    """
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    password: str = Field(max_length=255)  # 哈希后的密码
    role: UserRole = Field(default=UserRole.STUDENT)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    teacher_profile: Optional["Teacher"] = Relationship(back_populates="user")
    student_profile: Optional["Student"] = Relationship(back_populates="user")
    courses_as_teacher: List["Course"] = Relationship(back_populates="teacher")


class Teacher(SQLModel, table=True):
    """
    教师详情表
    存储教师的详细信息，通过 user_id 关联 User
    """
    __tablename__ = "teachers"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", unique=True, index=True)
    teacher_no: str = Field(unique=True, index=True, max_length=50)  # 工号
    name: str = Field(max_length=100)
    gender: Gender = Field(default=Gender.MALE)
    email: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    user: Optional[User] = Relationship(back_populates="teacher_profile")


class Student(SQLModel, table=True):
    """
    学生详情表
    存储学生的详细信息，通过 user_id 关联 User
    """
    __tablename__ = "students"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", unique=True, index=True)
    student_no: str = Field(unique=True, index=True, max_length=50)  # 学号
    name: str = Field(max_length=100)
    class_name: str = Field(max_length=50)  # 班级 (避免使用 class 关键字)
    gender: Gender = Field(default=Gender.MALE)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    user: Optional[User] = Relationship(back_populates="student_profile")
    submissions: List["HomeworkSubmission"] = Relationship(back_populates="student")


class Course(SQLModel, table=True):
    """
    课程表
    """
    __tablename__ = "courses"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(sa_column=Column(Text))
    teacher_id: str = Field(foreign_key="users.id", index=True)
    student_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    teacher: Optional[User] = Relationship(back_populates="courses_as_teacher")
    homeworks: List["Homework"] = Relationship(back_populates="course")
    folders: List["CourseFolder"] = Relationship(back_populates="course")


class Homework(SQLModel, table=True):
    """
    作业表
    """
    __tablename__ = "homeworks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    course_id: str = Field(foreign_key="courses.id", index=True)
    title: str = Field(max_length=200)
    description: str = Field(sa_column=Column(Text))
    deadline: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 附件 (JSON 格式存储)
    # 结构: {"name": str, "type": str, "size": int, "content": str}
    attachment: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # 批改标准 (JSON 格式存储)
    # 结构: {"type": "text"|"file", "content": str, "file_name"?: str, "file_size"?: int}
    grading_criteria: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # 关系
    course: Optional[Course] = Relationship(back_populates="homeworks")
    submissions: List["HomeworkSubmission"] = Relationship(back_populates="homework")


class HomeworkSubmission(SQLModel, table=True):
    """
    作业提交表
    """
    __tablename__ = "homework_submissions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    homework_id: str = Field(foreign_key="homeworks.id", index=True)
    student_id: str = Field(foreign_key="students.id", index=True)
    content: str = Field(sa_column=Column(Text))
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    # 附件列表 (JSON 格式存储)
    # 结构: [{"name": str, "type": str, "size": int, "content": str}, ...]
    attachments: Optional[list] = Field(default=None, sa_column=Column(JSON))

    # 批改信息
    score: Optional[int] = Field(default=None, ge=0, le=100)
    feedback: Optional[str] = Field(default=None, sa_column=Column(Text))
    graded_at: Optional[datetime] = Field(default=None)

    # 关系
    homework: Optional[Homework] = Relationship(back_populates="submissions")
    student: Optional[Student] = Relationship(back_populates="submissions")


class CourseFolder(SQLModel, table=True):
    """
    课程文件夹表
    """
    __tablename__ = "course_folders"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    course_id: str = Field(foreign_key="courses.id", index=True)
    name: str = Field(max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    course: Optional[Course] = Relationship(back_populates="folders")
    files: List["CourseFile"] = Relationship(back_populates="folder")


class CourseFile(SQLModel, table=True):
    """
    课程文件表
    """
    __tablename__ = "course_files"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    folder_id: str = Field(foreign_key="course_folders.id", index=True)
    course_id: str = Field(foreign_key="courses.id", index=True)
    name: str = Field(max_length=255)
    size: int  # 文件大小 (字节)
    type: str = Field(max_length=100)  # MIME 类型
    content: str = Field(sa_column=Column(Text))  # Base64 编码的文件内容
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    folder: Optional[CourseFolder] = Relationship(back_populates="files")
