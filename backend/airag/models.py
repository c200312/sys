"""
AI RAG 数据模型定义
"""
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel


class KnowledgeSourceType:
    """知识来源类型"""
    PERSONAL = "personal"
    COURSE = "course"


class QueryType(Enum):
    """查询类型（用于智能路由）"""
    FACTUAL = "factual"        # 事实性问题，需要精确匹配
    CONCEPTUAL = "conceptual"  # 概念性问题，需要理解上下文
    SUMMARY = "summary"        # 总结性问题，需要大范围检索
    COMPARISON = "comparison"  # 对比性问题，需要多源检索


# ==================== 分块相关 ====================

@dataclass
class ChunkWithContext:
    """带上下文的分块"""
    small_chunk: str      # 小块（用于索引）
    large_chunk: str      # 大块（用于返回）
    metadata: Dict[str, Any]
    chunk_id: str


# ==================== API 请求/响应模型 ====================

class AddKnowledgeRequest(BaseModel):
    """添加知识库资源请求"""
    name: str
    content_base64: str
    file_type: str
    source_type: str = KnowledgeSourceType.PERSONAL
    course_id: Optional[str] = None
    course_file_id: Optional[str] = None


class KnowledgeItem(BaseModel):
    """知识库项目"""
    id: str
    name: str
    source_type: str
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    chunks_count: int
    created_at: str
    owner_id: Optional[str] = None


class ListKnowledgeRequest(BaseModel):
    """获取知识库列表请求"""
    course_ids: List[str] = []


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    knowledge_ids: List[str] = []
    history: List[Dict[str, str]] = []


class SourceItem(BaseModel):
    """源数据项"""
    name: str
    content: str
    course_name: Optional[str] = None
    score: Optional[float] = None  # 相关性分数


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool
    message: str = ""
    sources: List[SourceItem] = []
    retrieval_info: Optional[Dict[str, Any]] = None  # 检索信息（调试用）
    error: Optional[str] = None
