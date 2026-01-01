"""
文件解析器：支持多种文档格式
"""
import io
import logging

from pypdf import PdfReader
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)


class FileParser:
    """
    文件解析器

    支持的格式：
    - 文本文件：txt, md
    - PDF 文档：pdf
    - Word 文档：docx
    """

    # 支持的文件扩展名
    SUPPORTED_TEXT = {'txt', 'md'}
    SUPPORTED_PDF = {'pdf'}
    SUPPORTED_DOCX = {'docx'}

    @classmethod
    def parse(cls, filename: str, content_bytes: bytes) -> str:
        """
        解析文件内容

        Args:
            filename: 文件名（用于判断类型）
            content_bytes: 文件二进制内容

        Returns:
            解析后的文本内容
        """
        ext = filename.lower().split('.')[-1] if '.' in filename else ''

        try:
            if ext in cls.SUPPORTED_TEXT:
                return cls._parse_text(content_bytes)
            elif ext in cls.SUPPORTED_PDF:
                return cls._parse_pdf(content_bytes)
            elif ext in cls.SUPPORTED_DOCX:
                return cls._parse_docx(content_bytes)
            else:
                # 尝试作为文本解析
                return cls._parse_text(content_bytes)

        except Exception as e:
            logger.error(f"文件解析错误 [{filename}]: {e}")
            return ""

    @classmethod
    def _parse_text(cls, content_bytes: bytes) -> str:
        """解析纯文本文件"""
        return content_bytes.decode('utf-8', errors='ignore')

    @classmethod
    def _parse_pdf(cls, content_bytes: bytes) -> str:
        """解析 PDF 文件"""
        try:
            pdf_reader = PdfReader(io.BytesIO(content_bytes))
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return '\n\n'.join(text_parts)
        except Exception as e:
            logger.error(f"PDF 解析失败: {e}")
            return ""

    @classmethod
    def _parse_docx(cls, content_bytes: bytes) -> str:
        """解析 Word 文档"""
        try:
            doc = DocxDocument(io.BytesIO(content_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return '\n\n'.join(paragraphs)
        except Exception as e:
            logger.error(f"DOCX 解析失败: {e}")
            return ""

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """
        检查文件是否支持解析

        Args:
            filename: 文件名

        Returns:
            是否支持
        """
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        all_supported = cls.SUPPORTED_TEXT | cls.SUPPORTED_PDF | cls.SUPPORTED_DOCX
        return ext in all_supported


# 便捷函数
def parse_file_content(filename: str, content_bytes: bytes) -> str:
    """解析文件内容（便捷函数）"""
    return FileParser.parse(filename, content_bytes)
