"""
重排序模块：使用专业 Rerank 模型判断文档与问题的真实相关性

向量检索只能找到语义相近的文档，但无法准确判断是否真正相关。
重排序器使用交叉编码器直接计算 query-document 对的相关性分数，
能够更准确地过滤掉不相关的文档。

支持的 Rerank 模型：
- 阿里云百炼 gte-rerank（推荐）
- Cohere rerank
"""
import os
import logging
import requests
from typing import List, Tuple
from dataclasses import dataclass

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# 重排序相关性阈值：低于此分数的文档视为不相关
RERANK_THRESHOLD = 0.3


@dataclass
class RerankResult:
    """重排序结果"""
    document: Document
    original_score: float  # 原始检索分数
    rerank_score: float    # 重排序分数
    is_relevant: bool      # 是否相关


class DashScopeReranker:
    """
    基于阿里云百炼 gte-rerank 的重排序器

    使用专业的交叉编码器模型，比 LLM 更准确、更快速。
    """

    RERANK_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"

    def __init__(self, api_key: str = None, threshold: float = RERANK_THRESHOLD):
        """
        初始化重排序器

        Args:
            api_key: 阿里云百炼 API Key，如果不提供则从环境变量获取
            threshold: 相关性阈值，低于此分数视为不相关
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.threshold = threshold

        if not self.api_key:
            logger.warning("[RERANK] 未配置 DASHSCOPE_API_KEY，重排序功能将不可用")
        else:
            logger.info(f"[RERANK] 初始化 DashScope 重排序器，阈值: {threshold}")

    def rerank(
        self,
        query: str,
        documents: List[Tuple[Document, float]],
        top_k: int = None
    ) -> List[RerankResult]:
        """
        对检索结果进行重排序

        Args:
            query: 用户查询
            documents: 检索结果列表，每个元素是 (Document, score) 元组
            top_k: 返回的最大文档数，None 表示返回所有相关文档

        Returns:
            重排序结果列表，按相关性分数降序排列
        """
        if not documents:
            return []

        if not self.api_key:
            logger.warning("[RERANK] API Key 未配置，跳过重排序")
            return [
                RerankResult(
                    document=doc,
                    original_score=score,
                    rerank_score=score,
                    is_relevant=score >= self.threshold
                )
                for doc, score in documents
            ]

        logger.info(f"[RERANK] ========== 开始重排序 ==========")
        logger.info(f"[RERANK] 查询: {query}")
        logger.info(f"[RERANK] 待重排序文档数: {len(documents)}")

        # 准备文档内容
        doc_texts = []
        for doc, _ in documents:
            content = doc.metadata.get("large_chunk", doc.page_content)
            # 截取前 2000 字符
            content_truncated = content[:2000] if len(content) > 2000 else content
            doc_texts.append(content_truncated)

        try:
            # 调用 DashScope Rerank API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gte-rerank",
                "input": {
                    "query": query,
                    "documents": doc_texts
                },
                "parameters": {
                    "top_n": len(documents),
                    "return_documents": False
                }
            }

            response = requests.post(
                self.RERANK_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"[RERANK] API 调用失败: {response.status_code} - {response.text}")
                # 失败时返回原始结果
                return self._fallback_results(documents)

            result = response.json()
            logger.info(f"[RERANK] API 返回: {result}")

            # 解析结果
            rerank_results = result.get("output", {}).get("results", [])

            results = []
            for item in rerank_results:
                idx = item.get("index", 0)
                rerank_score = item.get("relevance_score", 0.0)

                if idx < len(documents):
                    doc, original_score = documents[idx]
                    is_relevant = rerank_score >= self.threshold

                    logger.info(f"[RERANK] 文档[{idx}]: {doc.metadata.get('name', '未知')[:30]}")
                    logger.info(f"[RERANK]   原始分数: {original_score:.4f}")
                    logger.info(f"[RERANK]   重排序分数: {rerank_score:.4f}")
                    logger.info(f"[RERANK]   是否相关: {is_relevant}")

                    results.append(RerankResult(
                        document=doc,
                        original_score=original_score,
                        rerank_score=rerank_score,
                        is_relevant=is_relevant
                    ))

            # 按重排序分数降序排列
            results.sort(key=lambda x: x.rerank_score, reverse=True)

            # 过滤不相关的文档
            relevant_results = [r for r in results if r.is_relevant]

            logger.info(f"[RERANK] ========== 重排序结束 ==========")
            logger.info(f"[RERANK] 相关文档数: {len(relevant_results)}/{len(results)}")

            # 应用 top_k 限制
            if top_k and len(relevant_results) > top_k:
                relevant_results = relevant_results[:top_k]

            return relevant_results

        except Exception as e:
            logger.error(f"[RERANK] 重排序失败: {e}", exc_info=True)
            return self._fallback_results(documents)

    def _fallback_results(self, documents: List[Tuple[Document, float]]) -> List[RerankResult]:
        """失败时的后备结果"""
        return [
            RerankResult(
                document=doc,
                original_score=score,
                rerank_score=score,
                is_relevant=score >= self.threshold
            )
            for doc, score in documents
        ]

    def rerank_simple(
        self,
        query: str,
        documents: List[Tuple[Document, float]],
        top_k: int = None
    ) -> List[Tuple[Document, float]]:
        """
        简化版重排序，返回与原始检索相同的格式

        Args:
            query: 用户查询
            documents: 检索结果列表
            top_k: 返回的最大文档数

        Returns:
            (Document, score) 元组列表，只包含相关文档
        """
        results = self.rerank(query, documents, top_k)
        return [(r.document, r.rerank_score) for r in results]


# 兼容旧接口
LLMReranker = DashScopeReranker
