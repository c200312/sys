"""
Services 模块
"""
from app.services.auth import AuthService
from app.services.teacher import TeacherService
from app.services.student import StudentService
from app.services.course import CourseService
from app.services.homework import HomeworkService
from app.services.submission import SubmissionService
from app.services.resource import ResourceService

__all__ = [
    "AuthService",
    "TeacherService",
    "StudentService",
    "CourseService",
    "HomeworkService",
    "SubmissionService",
    "ResourceService",
]
