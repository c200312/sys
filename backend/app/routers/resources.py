"""
课程资源路由
实现 /api/folders/* 和 /api/files/* 接口
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession
import base64

from app.core import DbSession, CurrentUserId
from app.core.exceptions import AppException
from app.services import ResourceService
from app.schemas import (
    FolderUpdateRequest,
    FileUploadRequest,
    FileUpdateRequest,
)

# 文件夹路由
folders_router = APIRouter(prefix="/api/folders", tags=["文件夹"])

# 文件路由
files_router = APIRouter(prefix="/api/files", tags=["文件"])


# ============= 文件夹接口 =============

@folders_router.get("/{folder_id}", status_code=status.HTTP_200_OK)
async def get_folder(
    folder_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取单个文件夹

    GET /api/folders/{folderId}
    """
    try:
        service = ResourceService(db)
        folder = await service.get_folder(folder_id)
        return {
            "success": True,
            "data": folder.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@folders_router.put("/{folder_id}", status_code=status.HTTP_200_OK)
async def update_folder(
    folder_id: str,
    request: FolderUpdateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    更新文件夹

    PUT /api/folders/{folderId}
    """
    try:
        service = ResourceService(db)
        folder = await service.update_folder(folder_id, request)
        return {
            "success": True,
            "data": folder.model_dump(),
            "message": "文件夹更新成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@folders_router.delete("/{folder_id}", status_code=status.HTTP_200_OK)
async def delete_folder(
    folder_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    删除文件夹

    DELETE /api/folders/{folderId}
    """
    try:
        service = ResourceService(db)
        await service.delete_folder(folder_id)
        return {
            "success": True,
            "message": "文件夹删除成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@folders_router.get("/{folder_id}/files", status_code=status.HTTP_200_OK)
async def get_folder_files(
    folder_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取文件列表

    GET /api/folders/{folderId}/files
    """
    try:
        service = ResourceService(db)
        result = await service.get_folder_files(folder_id)
        return {
            "success": True,
            "data": result.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@folders_router.post("/{folder_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_file(
    folder_id: str,
    request: FileUploadRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    上传文件

    POST /api/folders/{folderId}/files
    """
    try:
        service = ResourceService(db)
        file = await service.upload_file(folder_id, request)
        return {
            "success": True,
            "data": file.model_dump(),
            "message": "文件上传成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


# ============= 文件接口 =============

@files_router.get("/{file_id}", status_code=status.HTTP_200_OK)
async def get_file(
    file_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    获取单个文件

    GET /api/files/{fileId}
    """
    try:
        service = ResourceService(db)
        file = await service.get_file(file_id)
        return {
            "success": True,
            "data": file.model_dump()
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@files_router.put("/{file_id}", status_code=status.HTTP_200_OK)
async def update_file(
    file_id: str,
    request: FileUpdateRequest,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    更新文件

    PUT /api/files/{fileId}
    """
    try:
        service = ResourceService(db)
        file = await service.update_file(file_id, request)
        return {
            "success": True,
            "data": file.model_dump(),
            "message": "文件更新成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@files_router.delete("/{file_id}", status_code=status.HTTP_200_OK)
async def delete_file(
    file_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    删除文件

    DELETE /api/files/{fileId}
    """
    try:
        service = ResourceService(db)
        await service.delete_file(file_id)
        return {
            "success": True,
            "message": "文件删除成功"
        }
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@files_router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    db: DbSession,
    user_id: CurrentUserId
):
    """
    下载文件

    GET /api/files/{fileId}/download
    """
    try:
        service = ResourceService(db)
        file = await service.download_file(file_id)

        # 解码 Base64 内容
        try:
            content = base64.b64decode(file.content)
        except Exception:
            # 如果不是有效的 Base64，直接返回原始内容
            content = file.content.encode()

        return Response(
            content=content,
            media_type=file.type,
            headers={
                "Content-Disposition": f'attachment; filename="{file.name}"'
            }
        )
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
