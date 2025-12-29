"""
课程资源 Service（文件夹和文件）
"""
from typing import Optional, List

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


class ResourceService:
    """课程资源服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.folder_repo = FolderRepository(session)
        self.file_repo = FileRepository(session)
        self.course_repo = CourseRepository(session)

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

        # 删除文件夹内的所有文件
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
                    content=f.content,
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
            content=file.content,
            created_at=file.created_at
        )

    async def upload_file(
        self,
        folder_id: str,
        request: FileUploadRequest
    ) -> FileResponse:
        """上传文件"""
        folder = await self.folder_repo.get_by_id(folder_id)
        if not folder:
            raise NotFoundError("文件夹不存在")

        # 检查同名文件（可选，根据 /utils 实现）
        # if await self.file_repo.name_exists(folder_id, request.name):
        #     raise ConflictError("文件名已存在")

        file = CourseFile(
            folder_id=folder_id,
            course_id=folder.course_id,
            name=request.name,
            size=request.size,
            type=request.type,
            content=request.content
        )
        file = await self.file_repo.create(file)

        return FileResponse(
            id=file.id,
            folder_id=file.folder_id,
            course_id=file.course_id,
            name=file.name,
            size=file.size,
            type=file.type,
            content=file.content,
            created_at=file.created_at
        )

    async def update_file(
        self,
        file_id: str,
        request: FileUpdateRequest
    ) -> FileResponse:
        """更新文件"""
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise NotFoundError("文件不存在")

        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.content is not None:
            update_data["content"] = request.content

        if update_data:
            file = await self.file_repo.update(file, update_data)

        return FileResponse(
            id=file.id,
            folder_id=file.folder_id,
            course_id=file.course_id,
            name=file.name,
            size=file.size,
            type=file.type,
            content=file.content,
            created_at=file.created_at
        )

    async def delete_file(self, file_id: str) -> None:
        """删除文件"""
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise NotFoundError("文件不存在")

        await self.file_repo.delete(file)

    async def download_file(self, file_id: str) -> FileResponse:
        """下载文件（返回完整文件信息）"""
        return await self.get_file(file_id)
