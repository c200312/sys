"""
学生路由
实现 /api/students/* 接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import DbSession, CurrentUserId
from app.core.exceptions import AppException
from app.services import StudentService, CourseService, SubmissionService
from app.schemas import (
    StudentCreateRequest,
    StudentUpdateRequest,
)

router = APIRouter(prefix="/api/students", tags=["学生"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_students(
    db: DbSession,
    user_id: CurrentUserId,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    search: Optional[str] = Query(None),
    class_filter: Optional[str] = Query(None, alias="class")
):
    """
    获取学生列表

    GET /api/students
    """
    try:
        service = StudentService(db)
        result = await service.get_students(
            page=page,
            page_size=page_size,
            search=search,
            class_filter=class_filter
        )
        return {
            "success": True,
            "data": result.model_dump(by_alias=True)
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.get("/classes", status_code=status.HTTP_200_OK)
async def get_class_list(
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取班级列表
    注意：此接口基于 /utils 实现，docs 未明确定义
    """
    try:
        service = StudentService(db)
        classes = await service.get_class_list()
        return {
            "success": True,
            "data": {"classes": classes}
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.get("/user/{user_id_param}", status_code=status.HTTP_200_OK)
async def get_student_by_user_id(
    user_id_param: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    根据用户 ID 获取学生

    GET /api/students/user/{userId}
    """
    try:
        service = StudentService(db)
        student = await service.get_student_by_user_id(user_id_param)
        return {
            "success": True,
            "data": student.model_dump(by_alias=True)
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.get("/{student_id}", status_code=status.HTTP_200_OK)
async def get_student(
    student_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取单个学生

    GET /api/students/{studentId}
    """
    try:
        service = StudentService(db)
        student = await service.get_student(student_id)
        return {
            "success": True,
            "data": student.model_dump(by_alias=True)
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_student(
    request: StudentCreateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    创建学生

    POST /api/students
    """
    try:
        service = StudentService(db)
        student = await service.create_student(request)
        return {
            "success": True,
            "data": student.model_dump(by_alias=True),
            "message": "学生创建成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.put("/{student_id}", status_code=status.HTTP_200_OK)
async def update_student(
    student_id: str,
    request: StudentUpdateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    更新学生

    PUT /api/students/{studentId}
    """
    try:
        service = StudentService(db)
        student = await service.update_student(student_id, request)
        return {
            "success": True,
            "data": student.model_dump(by_alias=True),
            "message": "学生信息更新成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.delete("/{student_id}", status_code=status.HTTP_200_OK)
async def delete_student(
    student_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    删除学生

    DELETE /api/students/{studentId}
    """
    try:
        service = StudentService(db)
        await service.delete_student(student_id)
        return {
            "success": True,
            "message": "学生删除成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.get("/{student_id}/courses", status_code=status.HTTP_200_OK)
async def get_student_courses(
    student_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取学生的课程列表

    GET /api/students/{studentId}/courses
    """
    try:
        # 先验证学生存在
        student_service = StudentService(db)
        student = await student_service.get_student(student_id)

        # 获取学生的用户 ID
        from app.repositories import StudentRepository
        student_repo = StudentRepository(db)
        student_model = await student_repo.get_by_id(student_id)

        course_service = CourseService(db)
        result = await course_service.get_student_courses(student_model.user_id)

        return {
            "success": True,
            "data": result.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.get("/{student_id}/submissions", status_code=status.HTTP_200_OK)
async def get_student_submissions(
    student_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取学生的所有提交

    GET /api/students/{studentId}/submissions
    """
    try:
        service = SubmissionService(db)
        result = await service.get_student_submissions(student_id)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
