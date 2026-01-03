"""
全局依赖管理：LLM、向量存储、检索器等组件的统一管理

双索引策略：
- Detail Index: 原文分块索引，用于细节问题
- Summary Index: 文档摘要索引，用于全局问题
"""
import os
import logging

from fastapi import HTTPException
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document as LCDocument

from .retriever import HybridRetriever
from .router import QueryRouter
from .chunker import HierarchicalChunker
from .summarizer import DocumentSummarizer
from .reranker import LLMReranker

logger = logging.getLogger(__name__)

# 模块目录配置
MODULE_DIR = os.path.dirname(__file__)
CHROMA_PERSIST_DIR = os.path.join(MODULE_DIR, "chroma_db")
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

# ChromaDB 集合名称（双索引）
DETAIL_COLLECTION_NAME = "knowledge_detail_v4"   # 原文索引
SUMMARY_COLLECTION_NAME = "knowledge_summary_v4"  # 摘要索引


class Dependencies:
    """
    全局依赖管理器

    使用单例模式管理各组件实例，避免重复初始化

    双索引策略：
    - detail_chroma: 原文分块索引
    - summary_chroma: 文档摘要索引
    """

    _embeddings = None
    _detail_chroma = None    # 原文索引
    _summary_chroma = None   # 摘要索引
    _hybrid_retriever = None
    _query_router = None
    _chunker = HierarchicalChunker()
    _summarizer = None
    _reranker = None

    @classmethod
    def get_embeddings(cls, api_key: str = None) -> OpenAIEmbeddings:
        """获取嵌入模型"""
        if cls._embeddings:
            return cls._embeddings

        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise HTTPException(400, "OpenAI API Key not configured")

        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        cls._embeddings = OpenAIEmbeddings(
            base_url=base_url,
            api_key=key,
            model="text-embedding-3-small",
        )
        return cls._embeddings

    @classmethod
    def get_detail_chroma(cls) -> Chroma:
        """获取原文索引（Detail Index）"""
        if cls._detail_chroma:
            return cls._detail_chroma

        embeddings = cls.get_embeddings()
        cls._detail_chroma = Chroma(
            collection_name=DETAIL_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
        logger.info(f"[DEPS] 初始化原文索引: {DETAIL_COLLECTION_NAME}")
        return cls._detail_chroma

    @classmethod
    def get_summary_chroma(cls) -> Chroma:
        """获取摘要索引（Summary Index）"""
        if cls._summary_chroma:
            return cls._summary_chroma

        embeddings = cls.get_embeddings()
        cls._summary_chroma = Chroma(
            collection_name=SUMMARY_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
        logger.info(f"[DEPS] 初始化摘要索引: {SUMMARY_COLLECTION_NAME}")
        return cls._summary_chroma

    @classmethod
    def get_chroma(cls) -> Chroma:
        """获取原文索引（兼容旧接口）"""
        return cls.get_detail_chroma()

    @classmethod
    def get_hybrid_retriever(cls) -> HybridRetriever:
        """获取混合检索器（支持双索引）"""
        if cls._hybrid_retriever:
            return cls._hybrid_retriever

        detail_chroma = cls.get_detail_chroma()
        summary_chroma = cls.get_summary_chroma()
        embeddings = cls.get_embeddings()
        cls._hybrid_retriever = HybridRetriever(
            detail_chroma=detail_chroma,
            summary_chroma=summary_chroma,
            embeddings=embeddings
        )

        # 构建 BM25 索引
        cls._build_bm25_index()

        return cls._hybrid_retriever

    @classmethod
    def _build_bm25_index(cls):
        """构建 BM25 索引（仅原文索引）"""
        logger.info(f"[BM25] ========== 开始构建BM25索引 ==========")
        try:
            detail_chroma = cls.get_detail_chroma()
            all_data = detail_chroma.get(include=["documents", "metadatas"])

            if all_data and all_data.get("documents"):
                doc_count = len(all_data["documents"])
                logger.info(f"[BM25] 从原文索引获取到 {doc_count} 个文档")

                docs = [
                    LCDocument(page_content=doc, metadata=meta)
                    for doc, meta in zip(all_data["documents"], all_data["metadatas"])
                ]

                # 显示部分文档内容
                for i, doc in enumerate(docs[:3]):
                    preview = doc.page_content[:100].replace('\n', ' ')
                    logger.info(f"[BM25] 文档{i+1}预览: {preview}...")

                cls._hybrid_retriever.build_bm25_index(docs)
                logger.info(f"[BM25] BM25索引构建完成")
            else:
                logger.warning(f"[BM25] 原文索引中没有文档，跳过BM25索引构建")

        except Exception as e:
            logger.error(f"[BM25] 构建BM25索引失败: {e}", exc_info=True)

    @classmethod
    def rebuild_bm25_index(cls):
        """重建 BM25 索引（直接重建，不重新创建 retriever）"""
        logger.info(f"[BM25] ========== 触发BM25索引重建 ==========")
        if cls._hybrid_retriever:
            # 直接重建索引，不重新创建 retriever
            cls._build_bm25_index()
        else:
            # 如果 retriever 不存在，则创建
            cls.get_hybrid_retriever()

    @classmethod
    def get_query_router(cls) -> QueryRouter:
        """获取查询路由器"""
        if cls._query_router:
            return cls._query_router

        llm = cls.get_llm()
        cls._query_router = QueryRouter(llm)
        return cls._query_router

    @classmethod
    def get_llm(cls, api_key: str = None) -> ChatOpenAI:
        """获取 LLM 实例"""
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise HTTPException(400, "OpenAI API Key not configured")

        model = os.getenv("AIRAG_MODEL") or os.getenv("AIWRITING_MODEL") or "gpt-4o"
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        return ChatOpenAI(
            base_url=base_url,
            api_key=key,
            model=model,
            temperature=0.3,
        )

    @classmethod
    def get_chunker(cls) -> HierarchicalChunker:
        """获取分块器"""
        return cls._chunker

    @classmethod
    def get_summarizer(cls) -> DocumentSummarizer:
        """获取摘要生成器"""
        if cls._summarizer:
            return cls._summarizer

        llm = cls.get_llm()
        cls._summarizer = DocumentSummarizer(llm)
        return cls._summarizer

    @classmethod
    def get_reranker(cls) -> LLMReranker:
        """获取重排序器"""
        if cls._reranker:
            return cls._reranker

        cls._reranker = LLMReranker()
        return cls._reranker


# 便捷函数
def get_embeddings(api_key: str = None) -> OpenAIEmbeddings:
    return Dependencies.get_embeddings(api_key)


def get_detail_chroma() -> Chroma:
    """获取原文索引"""
    return Dependencies.get_detail_chroma()


def get_summary_chroma() -> Chroma:
    """获取摘要索引"""
    return Dependencies.get_summary_chroma()


def get_chroma() -> Chroma:
    """获取原文索引（兼容旧接口）"""
    return Dependencies.get_chroma()


def get_hybrid_retriever() -> HybridRetriever:
    return Dependencies.get_hybrid_retriever()


def get_query_router() -> QueryRouter:
    return Dependencies.get_query_router()


def get_llm(api_key: str = None) -> ChatOpenAI:
    return Dependencies.get_llm(api_key)


def get_chunker() -> HierarchicalChunker:
    return Dependencies.get_chunker()


def get_summarizer() -> DocumentSummarizer:
    return Dependencies.get_summarizer()


def get_reranker() -> LLMReranker:
    return Dependencies.get_reranker()


def rebuild_bm25_index():
    Dependencies.rebuild_bm25_index()
