"""
混合检索器：向量检索 + BM25 关键词检索
"""
import logging
from typing import List, Tuple

from langchain_core.documents import Document as LCDocument

logger = logging.getLogger(__name__)

# BM25 可选依赖
try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False
    logger.warning("rank_bm25 not installed, BM25 retrieval disabled")


class HybridRetriever:
    """
    混合检索器：结合向量语义检索和 BM25 关键词检索

    - 向量检索：捕获语义相似性
    - BM25 检索：捕获关键词精确匹配
    - 分数融合：加权合并两种检索结果
    """

    def __init__(self, chroma_collection, embeddings):
        """
        初始化混合检索器

        Args:
            chroma_collection: ChromaDB 向量存储实例
            embeddings: 嵌入模型
        """
        self.chroma = chroma_collection
        self.embeddings = embeddings
        self.bm25_index = None
        self.bm25_docs = []
        self.bm25_metadata = []

    def build_bm25_index(self, documents: List[LCDocument]):
        """
        构建 BM25 索引

        Args:
            documents: 文档列表
        """
        if not HAS_BM25:
            return

        self.bm25_docs = [doc.page_content for doc in documents]
        self.bm25_metadata = [doc.metadata for doc in documents]

        # 中文分词
        tokenized_docs = [self._tokenize(doc) for doc in self.bm25_docs]
        self.bm25_index = BM25Okapi(tokenized_docs)
        logger.info(f"BM25 索引构建完成，共 {len(documents)} 个文档")

    def _tokenize(self, text: str) -> List[str]:
        """
        简单分词：中文按字符，英文按空格

        Args:
            text: 输入文本

        Returns:
            分词结果
        """
        tokens = []
        current_word = ""
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                if current_word:
                    tokens.append(current_word.lower())
                    current_word = ""
                tokens.append(char)
            elif char.isalnum():
                current_word += char
            else:
                if current_word:
                    tokens.append(current_word.lower())
                    current_word = ""
        if current_word:
            tokens.append(current_word.lower())
        return tokens

    def retrieve(
        self,
        query: str,
        knowledge_ids: List[str],
        top_k: int = 5,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3
    ) -> List[Tuple[LCDocument, float]]:
        """
        执行混合检索

        Args:
            query: 查询文本
            knowledge_ids: 限制检索的知识库ID列表
            top_k: 返回结果数量
            vector_weight: 向量检索权重
            bm25_weight: BM25 检索权重

        Returns:
            (文档, 分数) 元组列表，按分数降序排列
        """
        results = {}

        # 1. 向量检索
        self._vector_search(query, knowledge_ids, top_k, vector_weight, results)

        # 2. BM25 检索
        self._bm25_search(query, knowledge_ids, bm25_weight, results)

        # 3. 合并分数并排序
        scored_results = []
        for doc_id, data in results.items():
            total_score = data["vector_score"] + data["bm25_score"]
            scored_results.append((data["doc"], total_score))

        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]

    def _vector_search(
        self,
        query: str,
        knowledge_ids: List[str],
        top_k: int,
        weight: float,
        results: dict
    ):
        """执行向量检索"""
        filter_condition = {"knowledge_id": {"$in": knowledge_ids}} if knowledge_ids else None
        try:
            vector_results = self.chroma.similarity_search_with_score(
                query=query,
                k=top_k * 2,  # 多检索一些用于融合
                filter=filter_condition
            )
            for doc, score in vector_results:
                doc_id = f"{doc.metadata.get('knowledge_id')}_{doc.metadata.get('chunk_index', 0)}"
                # 转换分数（ChromaDB 返回的是距离，越小越好）
                normalized_score = 1 / (1 + score)
                results[doc_id] = {
                    "doc": doc,
                    "vector_score": normalized_score * weight,
                    "bm25_score": 0
                }
        except Exception as e:
            logger.error(f"向量检索失败: {e}")

    def _bm25_search(
        self,
        query: str,
        knowledge_ids: List[str],
        weight: float,
        results: dict
    ):
        """执行 BM25 检索"""
        if not HAS_BM25 or not self.bm25_index or weight <= 0:
            return

        try:
            query_tokens = self._tokenize(query)
            bm25_scores = self.bm25_index.get_scores(query_tokens)

            # 归一化 BM25 分数
            max_score = max(bm25_scores) if max(bm25_scores) > 0 else 1
            for idx, score in enumerate(bm25_scores):
                if score > 0:
                    metadata = self.bm25_metadata[idx]
                    # 权限过滤
                    if knowledge_ids and metadata.get("knowledge_id") not in knowledge_ids:
                        continue

                    doc_id = f"{metadata.get('knowledge_id')}_{metadata.get('chunk_index', 0)}"
                    normalized_score = (score / max_score) * weight

                    if doc_id in results:
                        results[doc_id]["bm25_score"] = normalized_score
                    else:
                        results[doc_id] = {
                            "doc": LCDocument(
                                page_content=self.bm25_docs[idx],
                                metadata=metadata
                            ),
                            "vector_score": 0,
                            "bm25_score": normalized_score
                        }
        except Exception as e:
            logger.error(f"BM25 检索失败: {e}")
