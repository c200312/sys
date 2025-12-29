"""
作业提交路由
实现 /api/submissions/* 接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import DbSession, CurrentUserId
from app.core.exceptions import AppException
from app.services import SubmissionService
from app.schemas import (
    SubmissionUpdateRequest,
    GradeRequest,
)

router = APIRouter(prefix="/api/submissions", tags=["作业提交"])


@router.get("/{submission_id}", status_code=status.HTTP_200_OK)
async def get_submission(
    submission_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取单个提交

    GET /api/submissions/{submissionId}
    """
    try:
        service = SubmissionService(db)
        submission = await service.get_submission(submission_id)
        return {
            "success": True,
            "data": submission.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.put("/{submission_id}", status_code=status.HTTP_200_OK)
async def update_submission(
    submission_id: str,
    request: SubmissionUpdateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    更新提交

    PUT /api/submissions/{submissionId}
    """
    try:
        service = SubmissionService(db)
        submission = await service.update_submission(submission_id, request)
        return {
            "success": True,
            "data": submission.model_dump(),
            "message": "作业更新成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("/{submission_id}/grade", status_code=status.HTTP_200_OK)
async def grade_submission(
    submission_id: str,
    request: GradeRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    批改作业

    POST /api/submissions/{submissionId}/grade
    """
    try:
        service = SubmissionService(db)
        result = await service.grade_submission(submission_id, request)
        return {
            "success": True,
            "data": result.model_dump(),
            "message": "批改成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.delete("/{submission_id}", status_code=status.HTTP_200_OK)
async def delete_submission(
    submission_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    删除提交

    DELETE /api/submissions/{submissionId}
    """
    try:
        service = SubmissionService(db)
        await service.delete_submission(submission_id)
        return {
            "success": True,
            "message": "提交删除成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
