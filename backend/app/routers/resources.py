"""
课程资源路由
实现 /api/folders/* 和 /api/files/* 接口
"""
import asyncio
import base64
import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Dict

from app.core import DbSession, CurrentUserId, get_settings
from app.core.exceptions import AppException
from app.services import ResourceService
from app.schemas import (
    FolderUpdateRequest,
    FileUploadRequest,
    FileUpdateRequest,
)

# 配置日志
logger = logging.getLogger(__name__)

# 文件夹路由
folders_router = APIRouter(prefix="/api/folders", tags=["文件夹"])

# 文件路由
files_router = APIRouter(prefix="/api/files", tags=["文件"])


def create_background_task(coro, task_name: str = "background_task"):
    """
    创建后台任务并添加异常处理回调
    确保后台任务的异常被正确记录
    """
    task = asyncio.create_task(coro)

    def handle_task_result(t):
        try:
            # 获取任务结果，如果有异常会抛出
            t.result()
        except asyncio.CancelledError:
            logger.info(f"[BACKGROUND] 任务被取消: {task_name}")
        except Exception as e:
            logger.error(f"[BACKGROUND] 任务执行失败: {task_name}, 错误: {e}", exc_info=True)

    task.add_done_callback(handle_task_result)
    return task


async def add_to_rag_knowledge(
    file_data: bytes,
    file_name: str,
    course_id: str,
    course_name: str,
    file_id: str,
    user_id: str = "system"  # 课程资源使用 system 用户
):
    """
    异步添加文件到 RAG 知识库
    """
    logger.info(f"[RAG] 开始添加课程资源到知识库: file_name={file_name}, course_id={course_id}, file_id={file_id}, user_id={user_id}")

    try:
        settings = get_settings()
        rag_url = f"http://localhost:{settings.airag_port}"

        logger.info(f"[RAG] RAG 服务地址: {rag_url}/knowledge/add-from-course")

        # 准备 FormData
        files = {
            'file_content': (file_name, file_data, 'application/octet-stream')
        }
        data = {
            'course_id': course_id,
            'course_name': course_name,
            'file_id': file_id,
            'file_name': file_name,
        }

        logger.info(f"[RAG] 发送请求到 RAG 服务: data={data}, file_size={len(file_data)} bytes")

        # 添加 headers
        headers = {
            'x-user-id': user_id
        }

        # PDF/PPT 使用 VLM 解析可能需要较长时间，设置 10 分钟超时
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{rag_url}/knowledge/add-from-course",
                files=files,
                data=data,
                headers=headers
            )

            logger.info(f"[RAG] RAG 服务响应状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                logger.info(f"[RAG] 成功添加课程资源到知识库: {file_name}, result={result}")
            else:
                logger.error(f"[RAG] 添加失败: {file_name}, 状态码: {response.status_code}, 响应: {response.text}")
    except Exception as e:
        logger.error(f"[RAG] 添加课程资源到知识库失败: {file_name}, 错误: {e}", exc_info=True)


async def delete_from_rag_knowledge(
    course_id: str,
    file_id: str,
    user_id: str = "system"
) -> bool:
    """
    从 RAG 知识库删除文件
    返回 True 表示删除成功，False 表示删除失败
    """
    # 知识库 ID 格式: course_{course_id}_{file_id}
    knowledge_id = f"course_{course_id}_{file_id}"
    logger.info(f"[RAG] 开始从知识库删除: knowledge_id={knowledge_id}, course_id={course_id}, file_id={file_id}")

    try:
        settings = get_settings()
        rag_url = f"http://localhost:{settings.airag_port}"

        headers = {
            'x-user-id': user_id
        }

        delete_url = f"{rag_url}/knowledge/{knowledge_id}"
        logger.info(f"[RAG] 删除请求 URL: {delete_url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                delete_url,
                headers=headers
            )

            logger.info(f"[RAG] RAG 删除响应状态码: {response.status_code}, 响应: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"[RAG] 成功从知识库删除: knowledge_id={knowledge_id}")
                    return True
                else:
                    # 如果资源不存在，也认为是成功的（可能之前没有添加成功）
                    error = result.get('error', '')
                    if '不存在' in error:
                        logger.info(f"[RAG] 资源不存在于知识库，跳过删除: knowledge_id={knowledge_id}")
                        return True
                    logger.warning(f"[RAG] 删除失败: knowledge_id={knowledge_id}, 错误: {error}")
                    return False
            else:
                logger.warning(f"[RAG] 删除失败: knowledge_id={knowledge_id}, 状态码: {response.status_code}, 响应: {response.text}")
                return False
    except httpx.ConnectError:
        logger.warning(f"[RAG] 无法连接到 RAG 服务，跳过知识库删除: knowledge_id={knowledge_id}")
        return True  # RAG 服务未运行时，不阻止文件删除
    except Exception as e:
        logger.error(f"[RAG] 从知识库删除失败: knowledge_id={knowledge_id}, 错误: {e}", exc_info=True)
        return False


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
    logger.info(f"[DELETE-FOLDER] 开始删除文件夹: folder_id={folder_id}, user_id={user_id}")

    try:
        service = ResourceService(db)

        # 获取文件夹信息和文件列表（用于后台 RAG 删除）
        folder = await service.folder_repo.get_by_id(folder_id)
        files_to_delete = []
        if folder and folder.course_id:
            files = await service.file_repo.get_by_folder_id(folder_id)
            files_to_delete = [(folder.course_id, f.id) for f in files]
            logger.info(f"[DELETE-FOLDER] 文件夹包含 {len(files)} 个文件")

        # 先删除文件夹（从数据库和 MinIO）
        await service.delete_folder(folder_id)

        # 后台异步删除每个文件对应的知识库内容（不阻塞响应）
        for course_id, file_id in files_to_delete:
            create_background_task(
                delete_from_rag_knowledge(
                    course_id=course_id,
                    file_id=file_id,
                    user_id="system"
                ),
                task_name=f"RAG删除-文件夹内文件-{file_id}"
            )
        if files_to_delete:
            logger.info(f"[DELETE-FOLDER] RAG 知识库删除已提交到后台: {len(files_to_delete)} 个文件")

        logger.info(f"[DELETE-FOLDER] 文件夹删除成功: folder_id={folder_id}")

        return {
            "success": True,
            "message": "文件夹删除成功"
        }
    except AppException as e:
        logger.error(f"[DELETE-FOLDER] 删除失败: {e.message}")
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
    logger.info(f"[UPLOAD] 开始上传文件: folder_id={folder_id}, file_name={request.name}, user_id={user_id}")

    try:
        service = ResourceService(db)
        file = await service.upload_file(folder_id, request)
        logger.info(f"[UPLOAD] 文件已保存到数据库: file_id={file.id}, name={file.name}")

        # 获取课程信息用于后台 RAG 同步
        folder = await service.folder_repo.get_by_id(folder_id)
        if folder and folder.course_id:
            course = await service.course_repo.get_by_id(folder.course_id)
            course_name = course.name if course else "未知课程"
            logger.info(f"[UPLOAD] 课程信息: course_id={folder.course_id}, course_name={course_name}")

            # 解码 Base64 内容
            file_data = base64.b64decode(
                request.content.split(",", 1)[1] if "," in request.content else request.content
            )

            # 后台异步添加到 RAG 知识库（不阻塞响应）
            create_background_task(
                add_to_rag_knowledge(
                    file_data,
                    file.name,
                    folder.course_id,
                    course_name,
                    file.id,
                    user_id
                ),
                task_name=f"RAG添加-{file.name}"
            )
            logger.info(f"[UPLOAD] RAG 知识库同步已提交到后台")
        else:
            logger.warning(f"[UPLOAD] 无法获取课程信息，跳过 RAG 同步: folder={folder}")

        return {
            "success": True,
            "data": file.model_dump(),
            "message": "文件上传成功"
        }
    except AppException as e:
        logger.error(f"[UPLOAD] 上传失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
    except Exception as e:
        logger.error(f"[UPLOAD] 上传异常: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": str(e)}
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
    logger.info(f"[DELETE] 开始删除文件: file_id={file_id}, user_id={user_id}")

    try:
        service = ResourceService(db)

        # 在删除前获取文件信息（用于 RAG 删除）
        file = await service.file_repo.get_by_id(file_id)
        course_id = file.course_id if file else None

        if file:
            logger.info(f"[DELETE] 文件信息: file_id={file.id}, name={file.name}, course_id={file.course_id}")
        else:
            logger.warning(f"[DELETE] 文件不存在: file_id={file_id}")

        # 删除文件（从数据库和 MinIO）
        await service.delete_file(file_id)

        # 后台异步从 RAG 知识库删除（不阻塞响应）
        if course_id:
            create_background_task(
                delete_from_rag_knowledge(
                    course_id=course_id,
                    file_id=file_id,
                    user_id="system"
                ),
                task_name=f"RAG删除-{file_id}"
            )
            logger.info(f"[DELETE] RAG 知识库删除已提交到后台")

        logger.info(f"[DELETE] 文件删除成功: file_id={file_id}")

        return {
            "success": True,
            "message": "文件删除成功"
        }
    except AppException as e:
        logger.error(f"[DELETE] 删除失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
    except Exception as e:
        logger.error(f"[DELETE] 删除异常: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": str(e)}
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
        content, filename, content_type = await service.download_file(file_id)

        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"success": False, "error": e.message, "code": e.code}
        )
