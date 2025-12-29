"""
通用响应模式
统一 API 响应格式
"""
from typing import Generic, TypeVar, Optional, Any, List

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """成功响应"""
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    code: str


class PaginatedData(BaseModel, Generic[T]):
    """分页数据"""
    items: List[T]
    total: int
    page: int
    page_size: int


# 通用分页参数
class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 20
