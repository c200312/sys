"""
智能查询路由器：根据问题类型优化检索策略
"""
from typing import Dict, Any

from .models import QueryType


class QueryRouter:
    """
    智能查询路由器

    根据查询内容自动分类问题类型，并返回优化的检索参数：
    - 事实性问题：精确匹配，少量结果
    - 概念性问题：语义理解，适中结果
    - 总结性问题：广泛检索，大量结果
    - 对比性问题：多源检索，多样结果
    """

    # 查询类型关键词映射
    QUERY_KEYWORDS = {
        QueryType.SUMMARY: ['总结', '概括', '归纳', '综述', 'summary', '整体', '主要内容', '概述'],
        QueryType.COMPARISON: ['对比', '比较', '区别', '不同', 'vs', '相比', '差异', '异同'],
        QueryType.CONCEPTUAL: ['什么是', '为什么', '如何', '怎么', '原理', '概念', '定义', '解释', '含义'],
    }

    # 检索参数配置
    RETRIEVAL_PARAMS = {
        QueryType.FACTUAL: {
            "top_k": 3,
            "vector_weight": 0.8,
            "bm25_weight": 0.2,
            "use_large_chunk": False
        },
        QueryType.CONCEPTUAL: {
            "top_k": 5,
            "vector_weight": 0.7,
            "bm25_weight": 0.3,
            "use_large_chunk": True
        },
        QueryType.SUMMARY: {
            "top_k": 8,
            "vector_weight": 0.6,
            "bm25_weight": 0.4,
            "use_large_chunk": True
        },
        QueryType.COMPARISON: {
            "top_k": 6,
            "vector_weight": 0.7,
            "bm25_weight": 0.3,
            "use_large_chunk": True
        }
    }

    def __init__(self, llm=None):
        """
        初始化路由器

        Args:
            llm: 可选的 LLM 实例（预留高级分类功能）
        """
        self.llm = llm

    def classify_query(self, query: str) -> QueryType:
        """
        分类查询类型

        Args:
            query: 用户查询文本

        Returns:
            查询类型枚举
        """
        query_lower = query.lower()

        # 按优先级检查关键词
        for query_type, keywords in self.QUERY_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                return query_type

        # 默认为事实性问题
        return QueryType.FACTUAL

    def get_retrieval_params(self, query_type: QueryType) -> Dict[str, Any]:
        """
        获取检索参数

        Args:
            query_type: 查询类型

        Returns:
            检索参数字典
        """
        return self.RETRIEVAL_PARAMS.get(query_type, self.RETRIEVAL_PARAMS[QueryType.FACTUAL])

    def route(self, query: str) -> tuple[QueryType, Dict[str, Any]]:
        """
        路由查询：分类并返回参数

        Args:
            query: 用户查询文本

        Returns:
            (查询类型, 检索参数) 元组
        """
        query_type = self.classify_query(query)
        params = self.get_retrieval_params(query_type)
        return query_type, params


# 默认路由器实例
default_router = QueryRouter()
