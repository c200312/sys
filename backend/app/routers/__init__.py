"""
Routers 模块
"""
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.teachers import router as teachers_router
from app.routers.students import router as students_router
from app.routers.courses import router as courses_router
from app.routers.homeworks import router as homeworks_router
from app.routers.submissions import router as submissions_router
from app.routers.resources import folders_router, files_router

__all__ = [
    "auth_router",
    "users_router",
    "teachers_router",
    "students_router",
    "courses_router",
    "homeworks_router",
    "submissions_router",
    "folders_router",
    "files_router",
]
