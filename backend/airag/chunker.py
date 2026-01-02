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
        语义感知分块：优先按 Markdown 标题分割，然后按段落分割

        Args:
            text: 文本内容
            chunk_size: 目标分块大小

        Returns:
            分块列表
        """
        # 先按语义单元解析
        semantic_units = self._parse_semantic_units(text)
        chunks = []
        current_chunk = ""

        for unit in semantic_units:
            unit_text = unit["text"]
            unit_type = unit["type"]

            # 主要标题（## 及以上）强制作为新块的开始
            is_major_heading = (
                unit_type == "heading" and
                unit.get("level", 99) <= 2
            )

            if is_major_heading and current_chunk.strip():
                # 遇到主要标题，先保存当前块
                chunks.append(current_chunk.strip())
                current_chunk = unit_text + "\n\n"
            elif len(current_chunk) + len(unit_text) + 2 <= chunk_size:
                # 累积到当前块
                current_chunk += ("\n\n" if current_chunk else "") + unit_text
            else:
                # 当前块已满，保存并开始新块
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # 如果单个单元超长，按句子分割
                if len(unit_text) > chunk_size:
                    sentence_chunks = self._split_by_sentences(unit_text, chunk_size)
                    chunks.extend(sentence_chunks)
                    current_chunk = ""
                else:
                    current_chunk = unit_text

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def _parse_semantic_units(self, text: str) -> List[Dict[str, Any]]:
        """
        解析文本为语义单元列表

        识别：
        - 标题（# ## ### 等）
        - 列表块（连续的 - * 或数字列表）
        - 普通段落

        Returns:
            语义单元列表，每个单元包含 type, text, level(可选)
        """
        units = []
        lines = text.split('\n')
        current_unit = {"type": "paragraph", "text": ""}
        in_list = False

        for line in lines:
            stripped = line.strip()

            # 空行：结束当前单元
            if not stripped:
                if current_unit["text"].strip():
                    units.append(current_unit)
                current_unit = {"type": "paragraph", "text": ""}
                in_list = False
                continue

            # 检测标题
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            if heading_match:
                # 保存之前的单元
                if current_unit["text"].strip():
                    units.append(current_unit)
                # 创建标题单元
                level = len(heading_match.group(1))
                units.append({
                    "type": "heading",
                    "level": level,
                    "text": stripped
                })
                current_unit = {"type": "paragraph", "text": ""}
                in_list = False
                continue

            # 检测列表项
            list_match = re.match(r'^[-*]\s+|^\d+\.\s+', stripped)
            if list_match:
                if not in_list:
                    # 开始新列表，保存之前的段落
                    if current_unit["text"].strip():
                        units.append(current_unit)
                    current_unit = {"type": "list", "text": stripped}
                    in_list = True
                else:
                    # 继续列表
                    current_unit["text"] += "\n" + stripped
                continue

            # 普通文本
            if in_list:
                # 列表结束，开始新段落
                if current_unit["text"].strip():
                    units.append(current_unit)
                current_unit = {"type": "paragraph", "text": stripped}
                in_list = False
            else:
                # 累积到当前段落
                if current_unit["text"]:
                    current_unit["text"] += "\n" + stripped
                else:
                    current_unit["text"] = stripped

        # 保存最后一个单元
        if current_unit["text"].strip():
            units.append(current_unit)

        return units

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
