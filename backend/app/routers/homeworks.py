"""
作业路由
实现 /api/homeworks/* 接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import DbSession, CurrentUserId
from app.core.exceptions import AppException
from app.services import HomeworkService, SubmissionService
from app.schemas import (
    HomeworkUpdateRequest,
    SubmissionCreateRequest,
)

router = APIRouter(prefix="/api/homeworks", tags=["作业"])


@router.get("/{homework_id}", status_code=status.HTTP_200_OK)
async def get_homework(
    homework_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取单个作业

    GET /api/homeworks/{homeworkId}
    """
    try:
        service = HomeworkService(db)
        homework = await service.get_homework(homework_id)
        return {
            "success": True,
            "data": homework.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.put("/{homework_id}", status_code=status.HTTP_200_OK)
async def update_homework(
    homework_id: str,
    request: HomeworkUpdateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    更新作业

    PUT /api/homeworks/{homeworkId}
    """
    try:
        service = HomeworkService(db)
        homework = await service.update_homework(homework_id, request)
        return {
            "success": True,
            "data": homework.model_dump(),
            "message": "作业更新成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.delete("/{homework_id}", status_code=status.HTTP_200_OK)
async def delete_homework(
    homework_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    删除作业

    DELETE /api/homeworks/{homeworkId}
    """
    try:
        service = HomeworkService(db)
        await service.delete_homework(homework_id)
        return {
            "success": True,
            "message": "作业删除成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


# ============= 作业提交 =============

@router.get("/{homework_id}/submissions", status_code=status.HTTP_200_OK)
async def get_homework_submissions(
    homework_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取作业提交列表

    GET /api/homeworks/{homeworkId}/submissions
    """
    try:
        service = SubmissionService(db)
        result = await service.get_homework_submissions(homework_id)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("/{homework_id}/submissions", status_code=status.HTTP_201_CREATED)
async def submit_homework(
    homework_id: str,
    request: SubmissionCreateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    提交作业

    POST /api/homeworks/{homeworkId}/submissions
    """
    try:
        # 获取学生 ID
        from app.repositories import StudentRepository
        student_repo = StudentRepository(db)
        student = await student_repo.get_by_user_id(user_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"success": False, "error": "学生不存在", "code": "RES_001"}
            )

        service = SubmissionService(db)
        submission = await service.create_submission(homework_id, student.id, request)
        return {
            "success": True,
            "data": submission.model_dump(),
            "message": "作业提交成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
