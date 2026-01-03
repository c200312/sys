"""
混合检索器：支持双索引策略

- Detail Index: 原文分块索引（向量 + BM25）
- Summary Index: 文档摘要索引（纯向量）
"""
import logging
from typing import List, Tuple, Optional

from langchain_core.documents import Document as LCDocument

from .models import IndexType

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
    混合检索器：支持双索引策略

    - 细节检索（Detail Index）：向量 + BM25 混合检索原文分块
    - 全局检索（Summary Index）：纯向量检索文档摘要
    """

    def __init__(
        self,
        detail_chroma,
        summary_chroma,
        embeddings,
        # 兼容旧接口
        chroma_collection=None
    ):
        """
        初始化混合检索器

        Args:
            detail_chroma: 原文索引的 ChromaDB 实例
            summary_chroma: 摘要索引的 ChromaDB 实例
            embeddings: 嵌入模型
        """
        self.detail_chroma = detail_chroma
        self.summary_chroma = summary_chroma
        self.embeddings = embeddings

        # BM25 索引（仅用于原文检索）
        self.bm25_index = None
        self.bm25_docs = []
        self.bm25_metadata = []

    def build_bm25_index(self, documents: List[LCDocument]):
        """
        构建 BM25 索引（仅原文）

        Args:
            documents: 文档列表
        """
        if not HAS_BM25:
            logger.warning(f"[BM25] rank_bm25 未安装，无法构建索引")
            return

        logger.info(f"[BM25] 开始构建索引，文档数: {len(documents)}")

        self.bm25_docs = [doc.page_content for doc in documents]
        self.bm25_metadata = [doc.metadata for doc in documents]

        # 中文分词
        tokenized_docs = [self._tokenize(doc) for doc in self.bm25_docs]

        # 显示分词示例
        if tokenized_docs:
            sample_tokens = tokenized_docs[0][:20]
            logger.info(f"[BM25] 分词示例(前20个): {sample_tokens}")

        self.bm25_index = BM25Okapi(tokenized_docs)
        logger.info(f"[BM25] 索引构建完成，共 {len(documents)} 个文档")

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
        index_type: IndexType = IndexType.DETAIL,
        top_k: int = 5,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        use_large_chunk: bool = True
    ) -> List[Tuple[LCDocument, float]]:
        """
        执行检索（根据索引类型选择不同策略）

        Args:
            query: 查询文本
            knowledge_ids: 限制检索的知识库ID列表
            index_type: 索引类型（DETAIL 或 SUMMARY）
            top_k: 返回结果数量
            vector_weight: 向量检索权重
            bm25_weight: BM25 检索权重
            use_large_chunk: 是否使用大块上下文

        Returns:
            (文档, 分数) 元组列表，按分数降序排列
        """
        logger.info(f"[RETRIEVER] ========== 开始检索 ==========")
        logger.info(f"[RETRIEVER] 查询: {query}")
        logger.info(f"[RETRIEVER] 索引类型: {index_type.value}")
        logger.info(f"[RETRIEVER] 知识库IDs: {knowledge_ids}")
        logger.info(f"[RETRIEVER] 参数: top_k={top_k}, vector_weight={vector_weight}, bm25_weight={bm25_weight}")

        if index_type == IndexType.SUMMARY:
            # 全局问题：从摘要索引检索
            return self._retrieve_from_summary(query, knowledge_ids, top_k, vector_weight)
        else:
            # 细节问题：从原文索引混合检索
            return self._retrieve_from_detail(
                query, knowledge_ids, top_k, vector_weight, bm25_weight, use_large_chunk
            )

    def _retrieve_from_summary(
        self,
        query: str,
        knowledge_ids: List[str],
        top_k: int,
        vector_weight: float
    ) -> List[Tuple[LCDocument, float]]:
        """
        从摘要索引检索（纯向量）

        检索块级摘要，聚合同一文档的相关块，返回完整上下文

        策略：
        1. 检索 top_k * 2 个摘要结果
        2. 按文档分组，聚合同一文档的多个相关块
        3. 返回聚合后的内容（最多 top_k 个文档）

        Args:
            query: 查询文本
            knowledge_ids: 知识库ID列表
            top_k: 返回数量
            vector_weight: 向量权重

        Returns:
            检索结果（聚合后的文档内容）
        """
        logger.info(f"[RETRIEVER] ----- 摘要索引检索（聚合模式） -----")

        filter_condition = {"knowledge_id": {"$in": knowledge_ids}} if knowledge_ids else None

        try:
            # 多检索一些用于聚合
            results = self.summary_chroma.similarity_search_with_score(
                query=query,
                k=top_k * 3,
                filter=filter_condition
            )

            logger.info(f"[RETRIEVER] 摘要检索原始结果: {len(results)} 条")

            # 按知识库ID分组聚合
            doc_groups = {}  # knowledge_id -> { chunks: [...], max_score: float, metadata: dict }

            for doc, score in results:
                kid = doc.metadata.get("knowledge_id", "unknown")
                normalized_score = (1 / (1 + score)) * vector_weight
                original_chunk = doc.metadata.get("original_chunk", doc.page_content)
                chunk_idx = doc.metadata.get("chunk_index", 0)

                if kid not in doc_groups:
                    doc_groups[kid] = {
                        "chunks": [],
                        "max_score": normalized_score,
                        "metadata": doc.metadata,
                        "summaries": []
                    }

                # 更新最高分
                if normalized_score > doc_groups[kid]["max_score"]:
                    doc_groups[kid]["max_score"] = normalized_score

                # 添加块（避免重复）
                existing_indices = [c["index"] for c in doc_groups[kid]["chunks"]]
                if chunk_idx not in existing_indices:
                    summary_text = doc.page_content  # 摘要内容
                    doc_groups[kid]["chunks"].append({
                        "index": chunk_idx,
                        "content": original_chunk,
                        "summary": summary_text,
                        "score": normalized_score
                    })
                    doc_groups[kid]["summaries"].append(summary_text)
                    logger.info(f"[RETRIEVER] 块{chunk_idx} 摘要: {summary_text[:150]}...")

            logger.info(f"[RETRIEVER] 聚合后文档数: {len(doc_groups)}")

            # 按最高分排序文档
            sorted_docs = sorted(
                doc_groups.items(),
                key=lambda x: x[1]["max_score"],
                reverse=True
            )[:top_k]

            final_results = []
            for kid, group in sorted_docs:
                # 按块索引排序，保持文档顺序
                sorted_chunks = sorted(group["chunks"], key=lambda x: x["index"])

                # 聚合块内容
                aggregated_content = "\n\n".join([c["content"] for c in sorted_chunks])

                name = group["metadata"].get("name", "unknown")
                logger.info(f"[RETRIEVER] 聚合文档: {name} (kid={kid})")
                logger.info(f"[RETRIEVER]   包含 {len(sorted_chunks)} 个块: {[c['index'] for c in sorted_chunks]}")
                logger.info(f"[RETRIEVER]   最高分: {group['max_score']:.4f}")
                logger.info(f"[RETRIEVER]   聚合内容长度: {len(aggregated_content)} 字符")
                logger.info(f"[RETRIEVER]   内容预览: {aggregated_content[:200]}...")

                result_doc = LCDocument(
                    page_content=aggregated_content,
                    metadata={
                        **group["metadata"],
                        "aggregated_chunks": len(sorted_chunks),
                        "chunk_indices": [c["index"] for c in sorted_chunks],
                        "summaries": group["summaries"],
                    }
                )
                final_results.append((result_doc, group["max_score"]))

            logger.info(f"[RETRIEVER] ========== 摘要检索结束: {len(final_results)} 个聚合文档 ==========")
            return final_results

        except Exception as e:
            logger.error(f"[RETRIEVER] 摘要索引检索失败: {e}", exc_info=True)
            return []

    def _retrieve_from_detail(
        self,
        query: str,
        knowledge_ids: List[str],
        top_k: int,
        vector_weight: float,
        bm25_weight: float,
        use_large_chunk: bool
    ) -> List[Tuple[LCDocument, float]]:
        """
        从原文索引混合检索（向量 + BM25）

        Args:
            query: 查询文本
            knowledge_ids: 知识库ID列表
            top_k: 返回数量
            vector_weight: 向量权重
            bm25_weight: BM25 权重
            use_large_chunk: 是否返回大块

        Returns:
            检索结果
        """
        logger.info(f"[RETRIEVER] ----- 原文索引混合检索 -----")

        results = {}

        # 1. 向量检索
        self._vector_search(query, knowledge_ids, top_k, vector_weight, results)
        vector_count = len(results)
        logger.info(f"[RETRIEVER] 向量检索结果: {vector_count} 条")

        # 2. BM25 检索
        self._bm25_search(query, knowledge_ids, bm25_weight, results)
        bm25_added = len(results) - vector_count
        logger.info(f"[RETRIEVER] BM25 新增结果: {bm25_added} 条")

        # 3. 合并分数并排序
        scored_results = []
        for doc_id, data in results.items():
            total_score = data["vector_score"] + data["bm25_score"]
            scored_results.append((data["doc"], total_score, data["vector_score"], data["bm25_score"]))

        scored_results.sort(key=lambda x: x[1], reverse=True)

        # 4. 去重：相同 large_chunk 只保留分数最高的
        seen_large_chunks = set()
        deduped_results = []
        for doc, total_score, vector_score, bm25_score in scored_results:
            # 用 large_chunk 的前 100 字符 + 文件名作为去重 key
            large_chunk = doc.metadata.get("large_chunk", doc.page_content)
            dedup_key = (doc.metadata.get("name", ""), large_chunk[:100] if large_chunk else "")

            if dedup_key in seen_large_chunks:
                logger.info(f"[RETRIEVER] 跳过重复大块: {doc.metadata.get('name', '未知')[:30]}")
                continue

            seen_large_chunks.add(dedup_key)
            deduped_results.append((doc, total_score, vector_score, bm25_score))

            if len(deduped_results) >= top_k:
                break

        logger.info(f"[RETRIEVER] 去重后结果: {len(scored_results)} -> {len(deduped_results)} 条")

        # 日志输出
        logger.info(f"[RETRIEVER] ========== 最终结果: {len(deduped_results)} 条 ==========")
        final_results = []
        for i, (doc, total_score, vector_score, bm25_score) in enumerate(deduped_results):
            name = doc.metadata.get("name", "unknown")
            kid = doc.metadata.get("knowledge_id", "unknown")
            content_preview = doc.page_content[:200].replace('\n', ' ')
            large_chunk = doc.metadata.get("large_chunk", "")
            large_preview = large_chunk[:200].replace('\n', ' ') if large_chunk else "(无大块)"
            logger.info(f"[RETRIEVER] ----- 结果 {i+1} -----")
            logger.info(f"[RETRIEVER] 文件: {name}")
            logger.info(f"[RETRIEVER] 知识库ID: {kid}")
            logger.info(f"[RETRIEVER] 综合分数: {total_score:.4f} (向量={vector_score:.3f}, BM25={bm25_score:.3f})")
            logger.info(f"[RETRIEVER] 小块内容({len(doc.page_content)}字):")
            logger.info(f"[RETRIEVER]   {content_preview}")
            if use_large_chunk and large_chunk:
                logger.info(f"[RETRIEVER] 大块内容({len(large_chunk)}字):")
                logger.info(f"[RETRIEVER]   {large_preview}")

            final_results.append((doc, total_score))

        logger.info(f"[RETRIEVER] ========== 检索结束 ==========")

        return final_results

    def _vector_search(
        self,
        query: str,
        knowledge_ids: List[str],
        top_k: int,
        weight: float,
        results: dict
    ):
        """执行向量检索（原文索引）"""
        filter_condition = {"knowledge_id": {"$in": knowledge_ids}} if knowledge_ids else None
        try:
            vector_results = self.detail_chroma.similarity_search_with_score(
                query=query,
                k=top_k * 2,  # 多检索一些用于融合
                filter=filter_condition
            )
            for doc, score in vector_results:
                doc_id = doc.metadata.get('chunk_id') or \
                    f"{doc.metadata.get('knowledge_id')}_{doc.metadata.get('large_chunk_index', 0)}_{doc.metadata.get('small_chunk_index', 0)}"
                normalized_score = 1 / (1 + score)
                results[doc_id] = {
                    "doc": doc,
                    "vector_score": normalized_score * weight,
                    "bm25_score": 0
                }
                logger.info(f"[VECTOR] 找到: doc_id={doc_id}, score={normalized_score:.4f}")
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
        logger.info(f"[BM25] ----- BM25检索开始 -----")
        logger.info(f"[BM25] 查询: {query}")
        logger.info(f"[BM25] 权重: {weight}")
        logger.info(f"[BM25] 索引状态: HAS_BM25={HAS_BM25}, index={self.bm25_index is not None}, docs={len(self.bm25_docs)}")

        if not HAS_BM25:
            logger.warning(f"[BM25] rank_bm25 未安装，跳过")
            return
        if not self.bm25_index:
            logger.warning(f"[BM25] 索引未构建，跳过")
            return
        if weight <= 0:
            logger.info(f"[BM25] 权重为0，跳过")
            return

        try:
            query_tokens = self._tokenize(query)
            logger.info(f"[BM25] 查询分词: {query_tokens}")

            bm25_scores = self.bm25_index.get_scores(query_tokens)

            # 找出所有非零分数
            nonzero_scores = [(idx, score) for idx, score in enumerate(bm25_scores) if score > 0]
            logger.info(f"[BM25] 非零分数文档数: {len(nonzero_scores)}")

            # 归一化 BM25 分数
            max_score = max(bm25_scores) if max(bm25_scores) > 0 else 1
            logger.info(f"[BM25] 最高分: {max_score}")

            matched_count = 0
            filtered_count = 0

            for idx, score in enumerate(bm25_scores):
                if score > 0:
                    metadata = self.bm25_metadata[idx]
                    kid = metadata.get("knowledge_id")

                    # 权限过滤
                    if knowledge_ids and kid not in knowledge_ids:
                        filtered_count += 1
                        continue

                    matched_count += 1
                    doc_id = metadata.get('chunk_id') or \
                        f"{kid}_{metadata.get('large_chunk_index', 0)}_{metadata.get('small_chunk_index', 0)}"
                    normalized_score = (score / max_score) * weight

                    # 显示匹配详情（前5个）
                    if matched_count <= 5:
                        content_preview = self.bm25_docs[idx][:100].replace('\n', ' ')
                        logger.info(f"[BM25] 匹配{matched_count}: doc_id={doc_id}")
                        logger.info(f"[BM25]   score={score:.4f} -> normalized={normalized_score:.4f}")
                        logger.info(f"[BM25]   知识库: {kid}")
                        logger.info(f"[BM25]   内容: {content_preview}...")

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

            logger.info(f"[BM25] 匹配结果: {matched_count} 条 (过滤掉 {filtered_count} 条)")
            logger.info(f"[BM25] ----- BM25检索结束 -----")

        except Exception as e:
            logger.error(f"[BM25] 检索失败: {e}", exc_info=True)
