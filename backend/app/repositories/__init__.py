"""
Repositories 模块
"""
from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.repositories.teacher import TeacherRepository
from app.repositories.student import StudentRepository
from app.repositories.course import CourseRepository, CourseEnrollmentRepository
from app.repositories.homework import HomeworkRepository
from app.repositories.submission import SubmissionRepository
from app.repositories.resource import FolderRepository, FileRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "TeacherRepository",
    "StudentRepository",
    "CourseRepository",
    "CourseEnrollmentRepository",
    "HomeworkRepository",
    "SubmissionRepository",
    "FolderRepository",
    "FileRepository",
]
