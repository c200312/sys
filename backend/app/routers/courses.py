"""
课程路由
实现 /api/courses/* 接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import DbSession, CurrentUserId, CurrentUserInfo
from app.core.exceptions import AppException
from app.services import CourseService, HomeworkService, ResourceService
from app.schemas import (
    CourseCreateRequest,
    CourseUpdateRequest,
    AddStudentRequest,
    BatchAddStudentsRequest,
    HomeworkCreateRequest,
    FolderCreateRequest,
)

router = APIRouter(prefix="/api/courses", tags=["课程"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_courses(
    db: DbSession,
    user_id: CurrentUserId,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """
    获取课程列表

    GET /api/courses
    """
    try:
        service = CourseService(db)
        result = await service.get_courses(
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


@router.get("/{course_id}", status_code=status.HTTP_200_OK)
async def get_course(
    course_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取单个课程

    GET /api/courses/{courseId}
    """
    try:
        service = CourseService(db)
        course = await service.get_course(course_id)
        return {
            "success": True,
            "data": course.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_course(
    request: CourseCreateRequest,
    db: DbSession,
    user_info: CurrentUserInfo
):
    """
    创建课程

    POST /api/courses
    """
    try:
        service = CourseService(db)
        course = await service.create_course(request, user_info["id"])
        return {
            "success": True,
            "data": course.model_dump(),
            "message": "课程创建成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.put("/{course_id}", status_code=status.HTTP_200_OK)
async def update_course(
    course_id: str,
    request: CourseUpdateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    更新课程

    PUT /api/courses/{courseId}
    """
    try:
        service = CourseService(db)
        course = await service.update_course(course_id, request)
        return {
            "success": True,
            "data": course.model_dump(),
            "message": "课程更新成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.delete("/{course_id}", status_code=status.HTTP_200_OK)
async def delete_course(
    course_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    删除课程

    DELETE /api/courses/{courseId}
    """
    try:
        service = CourseService(db)
        await service.delete_course(course_id)
        return {
            "success": True,
            "message": "课程删除成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


# ============= 课程学员管理 =============

@router.get("/{course_id}/students", status_code=status.HTTP_200_OK)
async def get_course_students(
    course_id: str,
    db: DbSession,
    user_id: CurrentUserId,
    page: int = Query(1, ge=1),
    page_size: int = Query(1000, ge=1, le=1000),
    search: Optional[str] = Query(None)
):
    """
    获取课程学员列表

    GET /api/courses/{courseId}/students
    """
    try:
        service = CourseService(db)
        result = await service.get_course_students(
            course_id=course_id,
            page=page,
            page_size=page_size,
            search=search
        )
        return {
            "success": True,
            "data": {
                "students": [s.model_dump(by_alias=True) for s in result["students"]],
                "total": result["total"],
                "page": result["page"],
                "page_size": result["page_size"]
            }
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("/{course_id}/students", status_code=status.HTTP_201_CREATED)
async def add_student_to_course(
    course_id: str,
    request: AddStudentRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    添加课程学员

    POST /api/courses/{courseId}/students
    """
    try:
        service = CourseService(db)
        result = await service.add_student_to_course(course_id, request.student_id)
        return {
            "success": True,
            "message": "学员添加成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("/{course_id}/students/batch", status_code=status.HTTP_201_CREATED)
async def batch_add_students(
    course_id: str,
    request: BatchAddStudentsRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    批量添加学员

    POST /api/courses/{courseId}/students/batch
    """
    try:
        service = CourseService(db)
        result = await service.batch_add_students(course_id, request.student_ids)
        return {
            "success": True,
            "data": result.model_dump(),
            "message": f"成功添加{result.added_count}名学员"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.delete("/{course_id}/students/{student_id}", status_code=status.HTTP_200_OK)
async def remove_student_from_course(
    course_id: str,
    student_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    移除课程学员

    DELETE /api/courses/{courseId}/students/{studentId}
    """
    try:
        service = CourseService(db)
        await service.remove_student_from_course(course_id, student_id)
        return {
            "success": True,
            "message": "学员移除成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


# ============= 课程作业 =============

@router.get("/{course_id}/homeworks", status_code=status.HTTP_200_OK)
async def get_course_homeworks(
    course_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取课程作业列表

    GET /api/courses/{courseId}/homeworks
    """
    try:
        service = HomeworkService(db)
        result = await service.get_course_homeworks(course_id)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("/{course_id}/homeworks", status_code=status.HTTP_201_CREATED)
async def create_homework(
    course_id: str,
    request: HomeworkCreateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    创建作业

    POST /api/courses/{courseId}/homeworks
    """
    try:
        service = HomeworkService(db)
        homework = await service.create_homework(course_id, request)
        return {
            "success": True,
            "data": homework.model_dump(),
            "message": "作业创建成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


# ============= 课程文件夹 =============

@router.get("/{course_id}/folders", status_code=status.HTTP_200_OK)
async def get_course_folders(
    course_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取文件夹列表

    GET /api/courses/{courseId}/folders
    """
    try:
        service = ResourceService(db)
        result = await service.get_course_folders(course_id)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("/{course_id}/folders", status_code=status.HTTP_201_CREATED)
async def create_folder(
    course_id: str,
    request: FolderCreateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    创建文件夹

    POST /api/courses/{courseId}/folders
    """
    try:
        service = ResourceService(db)
        folder = await service.create_folder(course_id, request)
        return {
            "success": True,
            "data": folder.model_dump(),
            "message": "文件夹创建成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.get("/{course_id}/resources", status_code=status.HTTP_200_OK)
async def get_course_resources(
    course_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取课程资源（文件夹带文件）
    注意：此接口基于 /utils 实现

    GET /api/courses/{courseId}/resources
    """
    try:
        service = ResourceService(db)
        result = await service.get_course_resources(course_id)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
