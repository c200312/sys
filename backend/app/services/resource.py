"""
课程资源 Service（文件夹和文件）
"""
import base64
from typing import Optional, Tuple

from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError, ConflictError
from app.models import CourseFolder, CourseFile
from app.repositories import (
    FolderRepository,
    FileRepository,
    CourseRepository,
)
from app.schemas import (
    FolderCreateRequest,
    FolderUpdateRequest,
    FileUploadRequest,
    FileUpdateRequest,
    FolderResponse,
    FolderWithFiles,
    FolderListResponse,
    FileResponse,
    FileWithoutContent,
    FileListResponse,
    CourseResourcesResponse,
)
from app.services.minio_service import get_minio_service


class ResourceService:
    """课程资源服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.folder_repo = FolderRepository(session)
        self.file_repo = FileRepository(session)
        self.course_repo = CourseRepository(session)
        self.minio = get_minio_service()

    # ============= 文件夹操作 =============

    async def get_course_folders(self, course_id: str) -> FolderListResponse:
        """获取课程文件夹列表"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        folders = await self.folder_repo.get_by_course_id(course_id)

        return FolderListResponse(
            folders=[
                FolderResponse(
                    id=f.id,
                    course_id=f.course_id,
                    name=f.name,
                    created_at=f.created_at
                ) for f in folders
            ],
            total=len(folders)
        )

    async def get_course_resources(self, course_id: str) -> CourseResourcesResponse:
        """
        获取课程资源（文件夹带文件）
        基于 /utils 实现
        """
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        folders = await self.folder_repo.get_by_course_id(course_id)

        result = []
        for folder in folders:
            files = await self.file_repo.get_by_folder_id(folder.id)
            result.append(
                FolderWithFiles(
                    id=folder.id,
                    course_id=folder.course_id,
                    name=folder.name,
                    created_at=folder.created_at,
                    files=[
                        FileWithoutContent(
                            id=f.id,
                            folder_id=f.folder_id,
                            course_id=f.course_id,
                            name=f.name,
                            size=f.size,
                            type=f.type,
                            created_at=f.created_at
                        ) for f in files
                    ]
                )
            )

        return CourseResourcesResponse(
            folders=result,
            total=len(result)
        )

    async def get_folder(self, folder_id: str) -> FolderResponse:
        """获取单个文件夹"""
        folder = await self.folder_repo.get_by_id(folder_id)
        if not folder:
            raise NotFoundError("文件夹不存在")

        return FolderResponse(
            id=folder.id,
            course_id=folder.course_id,
            name=folder.name,
            created_at=folder.created_at
        )

    async def create_folder(
        self,
        course_id: str,
        request: FolderCreateRequest
    ) -> FolderResponse:
        """创建文件夹"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("课程不存在")

        # 检查同名文件夹
        if await self.folder_repo.name_exists(course_id, request.name):
            raise ConflictError("文件夹名称已存在")

        folder = CourseFolder(
            course_id=course_id,
            name=request.name
        )
        folder = await self.folder_repo.create(folder)

        return FolderResponse(
            id=folder.id,
            course_id=folder.course_id,
            name=folder.name,
            created_at=folder.created_at
        )

    async def update_folder(
        self,
        folder_id: str,
        request: FolderUpdateRequest
    ) -> FolderResponse:
        """更新文件夹"""
        folder = await self.folder_repo.get_by_id(folder_id)
        if not folder:
            raise NotFoundError("文件夹不存在")

        if request.name is not None:
            # 检查同名文件夹
            if request.name != folder.name:
                if await self.folder_repo.name_exists(folder.course_id, request.name):
                    raise ConflictError("文件夹名称已存在")

            folder = await self.folder_repo.update(folder, {"name": request.name})

        return FolderResponse(
            id=folder.id,
            course_id=folder.course_id,
            name=folder.name,
            created_at=folder.created_at
        )

    async def delete_folder(self, folder_id: str) -> None:
        """删除文件夹（级联删除文件）"""
        folder = await self.folder_repo.get_by_id(folder_id)
        if not folder:
            raise NotFoundError("文件夹不存在")

        # 获取文件夹内的所有文件，删除 MinIO 中的对象
        files = await self.file_repo.get_by_folder_id(folder_id)
        for f in files:
            try:
                self.minio.delete_file(f.object_name)
            except Exception:
                pass  # 忽略删除错误

        # 删除文件夹内的所有文件记录
        await self.file_repo.delete_by_folder_id(folder_id)

        # 删除文件夹
        await self.folder_repo.delete(folder)

    # ============= 文件操作 =============

    async def get_folder_files(self, folder_id: str) -> FileListResponse:
        """获取文件夹文件列表"""
        folder = await self.folder_repo.get_by_id(folder_id)
        if not folder:
            raise NotFoundError("文件夹不存在")

        files = await self.file_repo.get_by_folder_id(folder_id)

        return FileListResponse(
            files=[
                FileResponse(
                    id=f.id,
                    folder_id=f.folder_id,
                    course_id=f.course_id,
                    name=f.name,
                    size=f.size,
                    type=f.type,
                    object_name=f.object_name,
                    url=self.minio.get_presigned_url(f.object_name),
                    created_at=f.created_at
                ) for f in files
            ],
            total=len(files)
        )

    async def get_file(self, file_id: str) -> FileResponse:
        """获取单个文件"""
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise NotFoundError("文件不存在")

        return FileResponse(
            id=file.id,
            folder_id=file.folder_id,
            course_id=file.course_id,
            name=file.name,
            size=file.size,
            type=file.type,
            object_name=file.object_name,
            url=self.minio.get_presigned_url(file.object_name),
            created_at=file.created_at
        )

    async def upload_file_multipart(
        self,
        folder_id: str,
        file: UploadFile
    ) -> FileResponse:
        """上传文件（multipart/form-data 方式）"""
        folder = await self.folder_repo.get_by_id(folder_id)
        if not folder:
            raise NotFoundError("文件夹不存在")

        # 读取文件内容
        file_data = await file.read()
        file_size = len(file_data)
        content_type = file.content_type or "application/octet-stream"

        # 上传到 MinIO（使用文件夹 ID 组织文件）
        object_name = self.minio.upload_file(
            file_data,
            file.filename,
            content_type,
            prefix="courses/",
            folder_id=folder_id
        )

        # 保存文件元数据到数据库
        db_file = CourseFile(
            folder_id=folder_id,
            course_id=folder.course_id,
            name=file.filename,
            size=file_size,
            type=content_type,
            object_name=object_name
        )
        db_file = await self.file_repo.create(db_file)

        return FileResponse(
            id=db_file.id,
            folder_id=db_file.folder_id,
            course_id=db_file.course_id,
            name=db_file.name,
            size=db_file.size,
            type=db_file.type,
            object_name=db_file.object_name,
            url=self.minio.get_presigned_url(db_file.object_name),
            created_at=db_file.created_at
        )

    async def upload_file(
        self,
        folder_id: str,
        request: FileUploadRequest
    ) -> FileResponse:
        """上传文件（Base64 JSON 方式，兼容旧接口）"""
        folder = await self.folder_repo.get_by_id(folder_id)
        if not folder:
            raise NotFoundError("文件夹不存在")

        # 解码 Base64 内容
        content = request.content
        if "," in content:
            # 处理 data:xxx;base64,xxx 格式
            content = content.split(",", 1)[1]

        try:
            file_data = base64.b64decode(content)
        except Exception:
            raise ValueError("无效的 Base64 编码")

        # 上传到 MinIO（使用文件夹 ID 组织文件）
        object_name = self.minio.upload_file(
            file_data,
            request.name,
            request.type,
            prefix="courses/",
            folder_id=folder_id
        )

        # 保存文件元数据到数据库
        db_file = CourseFile(
            folder_id=folder_id,
            course_id=folder.course_id,
            name=request.name,
            size=request.size,
            type=request.type,
            object_name=object_name
        )
        db_file = await self.file_repo.create(db_file)

        return FileResponse(
            id=db_file.id,
            folder_id=db_file.folder_id,
            course_id=db_file.course_id,
            name=db_file.name,
            size=db_file.size,
            type=db_file.type,
            object_name=db_file.object_name,
            url=self.minio.get_presigned_url(db_file.object_name),
            created_at=db_file.created_at
        )

    async def update_file(
        self,
        file_id: str,
        request: FileUpdateRequest
    ) -> FileResponse:
        """更新文件（仅支持更新文件名）"""
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise NotFoundError("文件不存在")

        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name

        if update_data:
            file = await self.file_repo.update(file, update_data)

        return FileResponse(
            id=file.id,
            folder_id=file.folder_id,
            course_id=file.course_id,
            name=file.name,
            size=file.size,
            type=file.type,
            object_name=file.object_name,
            url=self.minio.get_presigned_url(file.object_name),
            created_at=file.created_at
        )

    async def delete_file(self, file_id: str) -> None:
        """删除文件"""
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise NotFoundError("文件不存在")

        # 从 MinIO 删除文件
        try:
            self.minio.delete_file(file.object_name)
        except Exception:
            pass  # 忽略删除错误

        # 从数据库删除记录
        await self.file_repo.delete(file)

    async def download_file(self, file_id: str) -> Tuple[bytes, str, str]:
        """
        下载文件

        Returns:
            Tuple[bytes, str, str]: (文件内容, 文件名, MIME类型)
        """
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise NotFoundError("文件不存在")

        # 从 MinIO 下载文件
        file_data = self.minio.download_file(file.object_name)

        return file_data, file.name, file.type
