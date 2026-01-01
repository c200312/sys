"""
层级分块器：小索引大窗口策略
"""
import re
import logging
from typing import List, Dict, Any

from .models import ChunkWithContext

logger = logging.getLogger(__name__)


class HierarchicalChunker:
    """
    层级分块器：实现小索引大窗口策略

    - 小块（small_chunk）：用于精确索引匹配
    - 大块（large_chunk）：用于返回完整上下文
    """

    def __init__(
        self,
        small_chunk_size: int = 256,
        large_chunk_size: int = 1024,
        overlap: int = 50
    ):
        """
        初始化分块器

        Args:
            small_chunk_size: 小块大小（用于索引）
            large_chunk_size: 大块大小（用于返回）
            overlap: 分块重叠大小
        """
        self.small_chunk_size = small_chunk_size
        self.large_chunk_size = large_chunk_size
        self.overlap = overlap

    def create_hierarchical_chunks(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[ChunkWithContext]:
        """
        创建层级分块

        Args:
            content: 原始文本内容
            metadata: 文档元数据

        Returns:
            层级分块列表
        """
        knowledge_id = metadata.get('knowledge_id', 'unknown')
        filename = metadata.get('name', 'unknown')

        logger.info(f"[CHUNKER] ========== 开始分块 ==========")
        logger.info(f"[CHUNKER] 文件: {filename}")
        logger.info(f"[CHUNKER] 知识库ID: {knowledge_id}")
        logger.info(f"[CHUNKER] 原始内容长度: {len(content)} 字符")
        logger.info(f"[CHUNKER] 分块配置: small={self.small_chunk_size}, large={self.large_chunk_size}, overlap={self.overlap}")

        # 预处理：统一换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # 首先按段落分割成大块
        large_chunks = self._split_into_chunks(content, self.large_chunk_size)
        logger.info(f"[CHUNKER] 大块数量: {len(large_chunks)}")

        # 对每个大块，创建小块索引
        results = []
        for large_idx, large_chunk in enumerate(large_chunks):
            small_chunks = self._split_into_chunks(large_chunk, self.small_chunk_size)

            for small_idx, small_chunk in enumerate(small_chunks):
                chunk_id = f"{metadata.get('knowledge_id', 'unknown')}_{large_idx}_{small_idx}"
                results.append(ChunkWithContext(
                    small_chunk=small_chunk,
                    large_chunk=large_chunk,
                    metadata={
                        **metadata,
                        "large_chunk_index": large_idx,
                        "small_chunk_index": small_idx,
                        "total_large_chunks": len(large_chunks),
                    },
                    chunk_id=chunk_id
                ))

        logger.info(f"[CHUNKER] 总分块数: {len(results)}")
        logger.info(f"[CHUNKER] ----- 分块内容详情 -----")
        for i, chunk in enumerate(results):
            logger.info(f"[CHUNKER] 【分块 {i}】")
            logger.info(f"[CHUNKER]   小块({len(chunk.small_chunk)}字):")
            # 显示小块完整内容（限制300字）
            small_content = chunk.small_chunk[:300].replace('\n', '\n[CHUNKER]   ')
            logger.info(f"[CHUNKER]   {small_content}")
            if len(chunk.small_chunk) > 300:
                logger.info(f"[CHUNKER]   ... (省略 {len(chunk.small_chunk) - 300} 字)")
        logger.info(f"[CHUNKER] ========== 分块结束 ==========")

        return results

    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """
        智能分块：优先按段落分割，超长段落按句子分割

        Args:
            text: 文本内容
            chunk_size: 目标分块大小

        Returns:
            分块列表
        """
        # 按段落分割
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # 如果单个段落超长，按句子分割
                if len(para) > chunk_size:
                    sentence_chunks = self._split_by_sentences(para, chunk_size)
                    chunks.extend(sentence_chunks)
                    current_chunk = ""
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text]

    def _split_by_sentences(self, text: str, chunk_size: int) -> List[str]:
        """
        按句子分割超长段落

        Args:
            text: 段落文本
            chunk_size: 目标分块大小

        Returns:
            分块列表
        """
        # 按句子边界分割（保留分隔符）
        sentences = re.split(r'([。！？.!?])', text)
        chunks = []
        sentence_buffer = ""

        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            # 添加句子结束符
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]

            if len(sentence_buffer) + len(sentence) <= chunk_size:
                sentence_buffer += sentence
            else:
                if sentence_buffer:
                    chunks.append(sentence_buffer)
                sentence_buffer = sentence

        if sentence_buffer:
            chunks.append(sentence_buffer)

        return chunks


# 默认分块器实例
default_chunker = HierarchicalChunker()
