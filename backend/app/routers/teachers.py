"""
教师路由
实现 /api/teachers/* 接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import DbSession, CurrentUserId
from app.core.exceptions import AppException
from app.services import TeacherService, CourseService
from app.schemas import (
    TeacherCreateRequest,
    TeacherUpdateRequest,
)

router = APIRouter(prefix="/api/teachers", tags=["教师"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_teachers(
    db: DbSession,
    user_id: CurrentUserId,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """
    获取教师列表

    GET /api/teachers
    """
    try:
        service = TeacherService(db)
        result = await service.get_teachers(
            page=page,
            page_size=page_size,
            search=search
        )
        return {
            "success": True,
            "data": result.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.get("/user/{user_id_param}", status_code=status.HTTP_200_OK)
async def get_teacher_by_user_id(
    user_id_param: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    根据用户 ID 获取教师

    GET /api/teachers/user/{userId}
    """
    try:
        service = TeacherService(db)
        teacher = await service.get_teacher_by_user_id(user_id_param)
        return {
            "success": True,
            "data": teacher.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.get("/{teacher_id}", status_code=status.HTTP_200_OK)
async def get_teacher(
    teacher_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取单个教师

    GET /api/teachers/{teacherId}
    """
    try:
        service = TeacherService(db)
        teacher = await service.get_teacher(teacher_id)
        return {
            "success": True,
            "data": teacher.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_teacher(
    request: TeacherCreateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    创建教师

    POST /api/teachers
    """
    try:
        service = TeacherService(db)
        teacher = await service.create_teacher(request)
        return {
            "success": True,
            "data": teacher.model_dump(),
            "message": "教师创建成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.put("/{teacher_id}", status_code=status.HTTP_200_OK)
async def update_teacher(
    teacher_id: str,
    request: TeacherUpdateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    更新教师

    PUT /api/teachers/{teacherId}
    """
    try:
        service = TeacherService(db)
        teacher = await service.update_teacher(teacher_id, request)
        return {
            "success": True,
            "data": teacher.model_dump(),
            "message": "教师信息更新成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.delete("/{teacher_id}", status_code=status.HTTP_200_OK)
async def delete_teacher(
    teacher_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    删除教师

    DELETE /api/teachers/{teacherId}
    """
    try:
        service = TeacherService(db)
        await service.delete_teacher(teacher_id)
        return {
            "success": True,
            "message": "教师删除成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.get("/{teacher_id}/courses", status_code=status.HTTP_200_OK)
async def get_teacher_courses(
    teacher_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取教师的课程列表

    GET /api/teachers/{teacherId}/courses
    """
    try:
        # 先验证教师存在
        teacher_service = TeacherService(db)
        teacher = await teacher_service.get_teacher(teacher_id)

        # 获取教师的用户 ID（教师详情表的 user_id）
        from app.repositories import TeacherRepository
        teacher_repo = TeacherRepository(db)
        teacher_model = await teacher_repo.get_by_id(teacher_id)

        course_service = CourseService(db)
        result = await course_service.get_teacher_courses(teacher_model.user_id)

        return {
            "success": True,
            "data": result.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
