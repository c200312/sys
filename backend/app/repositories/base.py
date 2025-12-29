"""
基础 Repository 类
提供通用的 CRUD 操作
"""
from typing import Generic, TypeVar, Type, Optional, List, Any

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """基础仓库类"""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """根据 ID 获取单条记录"""
        statement = select(self.model).where(self.model.id == id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        """获取所有记录"""
        statement = select(self.model)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[List[Any]] = None
    ) -> tuple[List[ModelType], int]:
        """分页获取记录"""
        # 构建查询
        statement = select(self.model)
        count_statement = select(self.model)

        if filters:
            for f in filters:
                statement = statement.where(f)
                count_statement = count_statement.where(f)

        # 获取总数
        count_result = await self.session.execute(count_statement)
        total = len(list(count_result.scalars().all()))

        # 分页
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        result = await self.session.execute(statement)
        items = list(result.scalars().all())

        return items, total

    async def create(self, obj: ModelType) -> ModelType:
        """创建记录"""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType, data: dict) -> ModelType:
        """更新记录"""
        for key, value in data.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """删除记录"""
        await self.session.delete(obj)
        await self.session.flush()

    async def delete_by_id(self, id: str) -> bool:
        """根据 ID 删除记录"""
        obj = await self.get_by_id(id)
        if obj:
            await self.delete(obj)
            return True
        return False
