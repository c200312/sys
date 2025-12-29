"""
课程资源 Repository（文件夹和文件）
"""
from typing import Optional, List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import CourseFolder, CourseFile
from app.repositories.base import BaseRepository


class FolderRepository(BaseRepository[CourseFolder]):
    """文件夹仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(CourseFolder, session)

    async def get_by_course_id(self, course_id: str) -> List[CourseFolder]:
        """获取课程的所有文件夹"""
        statement = select(CourseFolder).where(CourseFolder.course_id == course_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_name(self, course_id: str, name: str) -> Optional[CourseFolder]:
        """根据名称获取文件夹"""
        statement = select(CourseFolder).where(
            CourseFolder.course_id == course_id,
            CourseFolder.name == name
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def name_exists(self, course_id: str, name: str) -> bool:
        """检查文件夹名称是否存在"""
        folder = await self.get_by_name(course_id, name)
        return folder is not None

    async def delete_by_course_id(self, course_id: str) -> int:
        """删除课程的所有文件夹"""
        folders = await self.get_by_course_id(course_id)
        count = len(folders)
        for folder in folders:
            await self.session.delete(folder)
        await self.session.flush()
        return count


class FileRepository(BaseRepository[CourseFile]):
    """文件仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(CourseFile, session)

    async def get_by_folder_id(self, folder_id: str) -> List[CourseFile]:
        """获取文件夹的所有文件"""
        statement = select(CourseFile).where(CourseFile.folder_id == folder_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_course_id(self, course_id: str) -> List[CourseFile]:
        """获取课程的所有文件"""
        statement = select(CourseFile).where(CourseFile.course_id == course_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_name(self, folder_id: str, name: str) -> Optional[CourseFile]:
        """根据名称获取文件"""
        statement = select(CourseFile).where(
            CourseFile.folder_id == folder_id,
            CourseFile.name == name
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def name_exists(self, folder_id: str, name: str) -> bool:
        """检查文件名称是否存在"""
        file = await self.get_by_name(folder_id, name)
        return file is not None

    async def delete_by_folder_id(self, folder_id: str) -> int:
        """删除文件夹的所有文件"""
        files = await self.get_by_folder_id(folder_id)
        count = len(files)
        for file in files:
            await self.session.delete(file)
        await self.session.flush()
        return count

    async def delete_by_course_id(self, course_id: str) -> int:
        """删除课程的所有文件"""
        files = await self.get_by_course_id(course_id)
        count = len(files)
        for file in files:
            await self.session.delete(file)
        await self.session.flush()
        return count
