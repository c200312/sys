"""
全局依赖管理：LLM、向量存储、检索器等组件的统一管理
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

logger = logging.getLogger(__name__)

# 模块目录配置
MODULE_DIR = os.path.dirname(__file__)
CHROMA_PERSIST_DIR = os.path.join(MODULE_DIR, "chroma_db")
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

# ChromaDB 集合名称
COLLECTION_NAME = "knowledge_base_v3"


class Dependencies:
    """
    全局依赖管理器

    使用单例模式管理各组件实例，避免重复初始化
    """

    _embeddings = None
    _chroma = None
    _hybrid_retriever = None
    _query_router = None
    _chunker = HierarchicalChunker()

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
    def get_chroma(cls) -> Chroma:
        """获取 ChromaDB 向量存储"""
        if cls._chroma:
            return cls._chroma

        embeddings = cls.get_embeddings()
        cls._chroma = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
        return cls._chroma

    @classmethod
    def get_hybrid_retriever(cls) -> HybridRetriever:
        """获取混合检索器"""
        if cls._hybrid_retriever:
            return cls._hybrid_retriever

        chroma = cls.get_chroma()
        embeddings = cls.get_embeddings()
        cls._hybrid_retriever = HybridRetriever(chroma, embeddings)

        # 构建 BM25 索引
        cls._build_bm25_index()

        return cls._hybrid_retriever

    @classmethod
    def _build_bm25_index(cls):
        """构建 BM25 索引"""
        try:
            chroma = cls.get_chroma()
            all_data = chroma.get(include=["documents", "metadatas"])
            if all_data and all_data.get("documents"):
                docs = [
                    LCDocument(page_content=doc, metadata=meta)
                    for doc, meta in zip(all_data["documents"], all_data["metadatas"])
                ]
                cls._hybrid_retriever.build_bm25_index(docs)
        except Exception as e:
            logger.error(f"构建 BM25 索引失败: {e}")

    @classmethod
    def rebuild_bm25_index(cls):
        """重建 BM25 索引"""
        cls._hybrid_retriever = None
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


# 便捷函数
def get_embeddings(api_key: str = None) -> OpenAIEmbeddings:
    return Dependencies.get_embeddings(api_key)


def get_chroma() -> Chroma:
    return Dependencies.get_chroma()


def get_hybrid_retriever() -> HybridRetriever:
    return Dependencies.get_hybrid_retriever()


def get_query_router() -> QueryRouter:
    return Dependencies.get_query_router()


def get_llm(api_key: str = None) -> ChatOpenAI:
    return Dependencies.get_llm(api_key)


def get_chunker() -> HierarchicalChunker:
    return Dependencies.get_chunker()


def rebuild_bm25_index():
    Dependencies.rebuild_bm25_index()
