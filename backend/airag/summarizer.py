"""
文档摘要生成器

层级摘要策略：
1. 对每个大块生成摘要
2. 返回块级摘要列表（用于存储到 Summary Index）
3. 可选：聚合生成文档级摘要

块级摘要存储到 Summary Index，检索时能匹配到更具体的内容
"""
import logging
from typing import List
from dataclasses import dataclass

from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

# 块级摘要提示词
CHUNK_SUMMARY_PROMPT = """请为以下文档片段生成一个简洁的摘要。

要求：
1. 提取该片段的核心内容和关键信息
2. 保留重要的专有名词、术语、人名、数据
3. 摘要长度控制在 100-200 字
4. 使用清晰、简洁的语言

只输出摘要内容，不要添加任何解释或标题。"""


@dataclass
class ChunkSummary:
    """块级摘要"""
    summary: str           # 摘要内容
    chunk_index: int       # 块索引
    original_chunk: str    # 原始块内容（用于引用）


class DocumentSummarizer:
    """
    文档摘要生成器 - 块级摘要策略

    流程：
    1. 将文档按大块分割
    2. 对每个大块生成摘要
    3. 返回块级摘要列表

    优势：
    - 长文档完整覆盖，不丢失信息
    - 检索时能匹配到具体的块摘要
    - 保留原始块内容用于引用展示
    """

    def __init__(self, llm, chunk_size: int = 2000):
        """
        初始化摘要生成器

        Args:
            llm: LangChain LLM 实例
            chunk_size: 分块大小（用于摘要生成）
        """
        self.llm = llm
        self.chunk_size = chunk_size

    def generate_chunk_summaries(self, content: str, filename: str = "") -> List[ChunkSummary]:
        """
        生成块级摘要列表

        Args:
            content: 文档完整内容
            filename: 文件名（可选，用于日志）

        Returns:
            块级摘要列表
        """
        logger.info(f"[SUMMARIZER] ========== 开始生成块级摘要 ==========")
        logger.info(f"[SUMMARIZER] 文件: {filename}")
        logger.info(f"[SUMMARIZER] 内容长度: {len(content)} 字符")

        try:
            # 分块
            chunks = self._split_content(content)
            logger.info(f"[SUMMARIZER] 分成 {len(chunks)} 个块")

            # 生成每个块的摘要
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"[SUMMARIZER] 生成块 {i+1}/{len(chunks)} 的摘要...")
                summary = self._generate_chunk_summary(chunk, i + 1, len(chunks))
                chunk_summaries.append(ChunkSummary(
                    summary=summary,
                    chunk_index=i,
                    original_chunk=chunk
                ))
                logger.info(f"[SUMMARIZER]   块 {i+1} 摘要: {summary[:100]}...")

            logger.info(f"[SUMMARIZER] 块级摘要生成完成，共 {len(chunk_summaries)} 个")
            logger.info(f"[SUMMARIZER] ========== 摘要生成结束 ==========")

            return chunk_summaries

        except Exception as e:
            logger.error(f"[SUMMARIZER] 摘要生成失败: {e}", exc_info=True)
            # 降级：返回原始内容的前500字作为单个摘要
            fallback = content[:500].strip()
            if len(content) > 500:
                fallback += "..."
            return [ChunkSummary(
                summary=fallback,
                chunk_index=0,
                original_chunk=content[:self.chunk_size]
            )]

    def generate_summary(self, content: str, filename: str = "") -> str:
        """
        生成文档摘要（兼容旧接口）

        返回所有块摘要的拼接，用于快速预览

        Args:
            content: 文档完整内容
            filename: 文件名

        Returns:
            文档摘要文本
        """
        chunk_summaries = self.generate_chunk_summaries(content, filename)
        # 拼接所有块摘要
        return "\n\n".join([cs.summary for cs in chunk_summaries])

    def _split_content(self, content: str) -> List[str]:
        """
        按语义边界分块：优先保持段落完整

        策略：
        1. 按段落分割
        2. 合并小段落直到接近 chunk_size
        3. 超长段落按句子分割，不硬截断

        Args:
            content: 原始内容

        Returns:
            块列表
        """
        chunks = []
        # 按段落分割（支持单换行和双换行）
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        current_chunk = ""
        for para in paragraphs:
            # 如果当前块加上这个段落不超限，合并
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                # 先保存当前块
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                # 处理当前段落
                if len(para) <= self.chunk_size:
                    # 段落不超限，作为新块的开始
                    current_chunk = para + "\n\n"
                else:
                    # 超长段落：按句子分割
                    sub_chunks = self._split_long_paragraph(para)
                    chunks.extend(sub_chunks[:-1])  # 前面的块直接加入
                    current_chunk = sub_chunks[-1] + "\n\n" if sub_chunks else ""

        # 处理最后一个块
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # 如果没有分出块，整个内容作为一块
        if not chunks:
            chunks = [content]

        return chunks

    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """
        按句子分割超长段落，保持语义完整

        Args:
            paragraph: 超长段落

        Returns:
            分割后的块列表
        """
        import re
        # 中英文句子分隔符
        sentence_endings = re.compile(r'([。！？.!?]+)')
        parts = sentence_endings.split(paragraph)

        # 重新组合句子（把标点和句子合并）
        sentences = []
        i = 0
        while i < len(parts):
            sentence = parts[i]
            if i + 1 < len(parts) and sentence_endings.match(parts[i + 1]):
                sentence += parts[i + 1]
                i += 2
            else:
                i += 1
            if sentence.strip():
                sentences.append(sentence.strip())

        # 合并句子成块
        chunks = []
        current = ""
        for sent in sentences:
            if len(current) + len(sent) + 1 <= self.chunk_size:
                current += sent + " "
            else:
                if current.strip():
                    chunks.append(current.strip())
                # 如果单个句子超长，直接加入（不再截断）
                current = sent + " "

        if current.strip():
            chunks.append(current.strip())

        return chunks if chunks else [paragraph]

    def _generate_chunk_summary(self, chunk: str, chunk_num: int, total_chunks: int) -> str:
        """
        生成块级摘要

        Args:
            chunk: 块内容
            chunk_num: 当前块编号
            total_chunks: 总块数

        Returns:
            块摘要
        """
        messages = [
            SystemMessage(content=CHUNK_SUMMARY_PROMPT),
            HumanMessage(content=f"这是文档的第 {chunk_num}/{total_chunks} 部分：\n\n{chunk}")
        ]
        response = self.llm.invoke(messages)
        return response.content.strip()


# 便捷函数
def generate_document_summary(llm, content: str, filename: str = "") -> str:
    """生成文档摘要（便捷函数）"""
    summarizer = DocumentSummarizer(llm)
    return summarizer.generate_summary(content, filename)
