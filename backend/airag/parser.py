"""
文件解析器：支持多种文档格式

解析策略：
- PDF: 使用 Qwen-VL 逐页解析图片（视觉识别）
- DOCX: 本地解析（python-docx）
- PPT/PPTX: 先转为 PDF，再通过 Qwen-VL 逐页解析图片
- TXT/MD: 直接读取文本
"""
import io
import os
import base64
import asyncio
import logging
import tempfile
from typing import Optional

import httpx
from pypdf import PdfReader
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

# API 配置
DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class FileParser:
    """
    文件解析器

    支持的格式：
    - 文本文件：txt, md（直接读取）
    - PDF 文档：pdf（Qwen-VL 视觉识别）
    - Word 文档：docx（本地解析）
    - PPT 文档：ppt, pptx（转 PDF 后用 Qwen-VL 解析）
    """

    # 支持的文件扩展名
    SUPPORTED_TEXT = {'txt', 'md'}
    SUPPORTED_DOCX = {'docx'}  # DOCX 本地解析
    SUPPORTED_QWEN_VL = {'pdf'}  # PDF 使用 Qwen-VL
    SUPPORTED_PPT = {'ppt', 'pptx'}

    @classmethod
    async def parse(cls, filename: str, content_bytes: bytes) -> str:
        """
        解析文件内容

        Args:
            filename: 文件名（用于判断类型）
            content_bytes: 文件二进制内容

        Returns:
            解析后的 Markdown 文本内容
        """
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        file_size = len(content_bytes)

        logger.info(f"[PARSER] ========== 开始解析文件 ==========")
        logger.info(f"[PARSER] 文件名: {filename}")
        logger.info(f"[PARSER] 扩展名: {ext}")
        logger.info(f"[PARSER] 文件大小: {file_size} bytes ({file_size/1024:.2f} KB)")

        try:
            if ext in cls.SUPPORTED_TEXT:
                logger.info(f"[PARSER] 解析方式: 直接读取文本")
                result = cls._parse_text(content_bytes)
            elif ext in cls.SUPPORTED_QWEN_VL:
                logger.info(f"[PARSER] 解析方式: Qwen-VL 视觉识别 (PDF)")
                result = await cls._parse_pdf_direct(content_bytes)
            elif ext in cls.SUPPORTED_DOCX:
                logger.info(f"[PARSER] 解析方式: 本地解析 (DOCX)")
                result = cls._local_parse_docx(content_bytes)
            elif ext in cls.SUPPORTED_PPT:
                logger.info(f"[PARSER] 解析方式: LibreOffice + Qwen-VL (PPT)")
                result = await cls._parse_ppt(filename, content_bytes)
            else:
                logger.info(f"[PARSER] 解析方式: 尝试作为文本解析 (未知类型)")
                result = cls._parse_text(content_bytes)

            logger.info(f"[PARSER] 解析完成: {len(result)} 字符")
            logger.info(f"[PARSER] ----- 解析内容预览(前500字) -----")
            preview_lines = result[:500].split('\n')
            for line in preview_lines:
                if line.strip():
                    logger.info(f"[PARSER]   {line}")
            if len(result) > 500:
                logger.info(f"[PARSER]   ... (省略 {len(result) - 500} 字)")
            logger.info(f"[PARSER] ========== 解析结束 ==========")
            return result

        except Exception as e:
            logger.error(f"[PARSER] 文件解析错误 [{filename}]: {e}", exc_info=True)
            # 降级到本地解析
            logger.info(f"[PARSER] 降级到本地解析...")
            return await cls._fallback_parse(filename, content_bytes)

    @classmethod
    def _parse_text(cls, content_bytes: bytes) -> str:
        """解析纯文本文件"""
        return content_bytes.decode('utf-8', errors='ignore')

    @classmethod
    async def _parse_pdf_direct(cls, content_bytes: bytes) -> str:
        """
        直接使用 Qwen-VL 解析 PDF 文件

        流程：
        1. PDF 转图片（每页）
        2. 使用 Qwen-VL 解析每页图片
        3. 合并所有页面的解析结果
        """
        logger.info(f"[PARSER] ----- PDF直接解析开始 -----")

        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            logger.warning("[PARSER] 阿里云 API Key 未配置，使用本地解析")
            return cls._local_parse_pdf(content_bytes)

        logger.info(f"[PARSER] DASHSCOPE_API_KEY 已配置")

        try:
            result = await cls._parse_pdf_with_qwen_vl(content_bytes, api_key)
            if result:
                return result
            else:
                logger.warning("[PARSER] Qwen-VL 解析结果为空，降级使用本地解析")
                return cls._local_parse_pdf(content_bytes)
        except Exception as e:
            logger.error(f"[PARSER] PDF解析失败: {e}", exc_info=True)
            return cls._local_parse_pdf(content_bytes)

    @classmethod
    async def _parse_ppt(cls, filename: str, content_bytes: bytes) -> str:
        """
        解析 PPT 文件

        流程：
        1. PPT 转 PDF（使用 LibreOffice）
        2. PDF 转图片（每页）
        3. 使用 Qwen-VL 解析每页图片
        4. 合并所有页面的解析结果
        """
        logger.info(f"[PARSER] ----- PPT解析开始 -----")

        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            logger.warning("[PARSER] 阿里云 API Key 未配置，使用本地解析")
            return await cls._fallback_parse(filename, content_bytes)

        logger.info(f"[PARSER] DASHSCOPE_API_KEY 已配置")

        try:
            # 将 PPT 保存为临时文件
            suffix = '.pptx' if filename.lower().endswith('.pptx') else '.ppt'
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_ppt:
                tmp_ppt.write(content_bytes)
                tmp_ppt_path = tmp_ppt.name

            logger.info(f"[PARSER] PPT临时文件: {tmp_ppt_path}")

            try:
                # 使用 LibreOffice 转换 PPT 为 PDF
                logger.info(f"[PARSER] 开始转换PPT为PDF...")
                pdf_bytes = await cls._convert_ppt_to_pdf(tmp_ppt_path)

                if pdf_bytes:
                    logger.info(f"[PARSER] PPT转PDF成功，PDF大小: {len(pdf_bytes)} bytes")
                    # PDF 转图片并解析
                    logger.info(f"[PARSER] 开始使用Qwen-VL解析PDF...")
                    return await cls._parse_pdf_with_qwen_vl(pdf_bytes, api_key)
                else:
                    # 降级：直接解析 PPT 文本
                    logger.warning(f"[PARSER] PPT转PDF失败，降级使用本地解析")
                    return await cls._fallback_parse(filename, content_bytes)

            finally:
                # 清理临时文件
                if os.path.exists(tmp_ppt_path):
                    os.unlink(tmp_ppt_path)
                    logger.info(f"[PARSER] 已清理临时文件")

        except Exception as e:
            logger.error(f"[PARSER] PPT解析失败: {e}", exc_info=True)
            return await cls._fallback_parse(filename, content_bytes)

    @classmethod
    async def _convert_ppt_to_pdf(cls, ppt_path: str) -> Optional[bytes]:
        """
        将 PPT 转换为 PDF

        尝试使用 LibreOffice（如果可用）
        """
        try:
            import subprocess
            import shutil

            # 创建临时输出目录
            output_dir = tempfile.mkdtemp()
            logger.info(f"[PARSER] LibreOffice输出目录: {output_dir}")

            try:
                # 尝试使用 LibreOffice
                # Windows: 检查常见安装路径, Linux/Mac: libreoffice
                soffice_cmd = None
                if os.name == "nt":
                    # Windows 常见安装路径
                    possible_paths = [
                        r"C:\Program Files\LibreOffice\program\soffice.exe",
                        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            soffice_cmd = path
                            logger.info(f"[PARSER] 找到LibreOffice: {path}")
                            break
                    if not soffice_cmd:
                        # 尝试 PATH 中的 soffice
                        soffice_cmd = "soffice"
                        logger.info(f"[PARSER] 使用PATH中的soffice")
                else:
                    soffice_cmd = "libreoffice"
                    logger.info(f"[PARSER] 使用libreoffice命令")

                logger.info(f"[PARSER] 执行LibreOffice转换命令...")
                result = subprocess.run(
                    [
                        soffice_cmd,
                        "--headless",
                        "--convert-to", "pdf",
                        "--outdir", output_dir,
                        ppt_path
                    ],
                    capture_output=True,
                    timeout=60
                )

                logger.info(f"[PARSER] LibreOffice返回码: {result.returncode}")
                if result.stdout:
                    logger.info(f"[PARSER] LibreOffice stdout: {result.stdout.decode('utf-8', errors='ignore')}")
                if result.stderr:
                    logger.warning(f"[PARSER] LibreOffice stderr: {result.stderr.decode('utf-8', errors='ignore')}")

                if result.returncode == 0:
                    # 查找生成的 PDF
                    pdf_filename = os.path.splitext(os.path.basename(ppt_path))[0] + ".pdf"
                    pdf_path = os.path.join(output_dir, pdf_filename)
                    logger.info(f"[PARSER] 预期PDF路径: {pdf_path}")

                    if os.path.exists(pdf_path):
                        logger.info(f"[PARSER] PDF文件存在，读取中...")
                        with open(pdf_path, 'rb') as f:
                            pdf_data = f.read()
                        logger.info(f"[PARSER] PDF读取成功，大小: {len(pdf_data)} bytes")
                        return pdf_data
                    else:
                        logger.warning(f"[PARSER] PDF文件不存在: {pdf_path}")
                        # 列出目录内容
                        dir_contents = os.listdir(output_dir)
                        logger.info(f"[PARSER] 输出目录内容: {dir_contents}")
                else:
                    logger.warning(f"[PARSER] LibreOffice转换失败，返回码: {result.returncode}")

            except FileNotFoundError as e:
                logger.warning(f"[PARSER] LibreOffice未安装或找不到: {e}")
            except subprocess.TimeoutExpired:
                logger.warning("[PARSER] PPT转PDF超时(60秒)")
            finally:
                # 清理临时目录
                shutil.rmtree(output_dir, ignore_errors=True)
                logger.info(f"[PARSER] 已清理临时输出目录")

        except Exception as e:
            logger.error(f"[PARSER] PPT转PDF失败: {e}", exc_info=True)

        return None

    @classmethod
    async def _parse_pdf_with_qwen_vl(cls, pdf_bytes: bytes, api_key: str) -> str:
        """
        使用 Qwen-VL 解析 PDF 的每一页

        1. PDF 转图片
        2. 每页图片发送给 Qwen-VL
        3. 合并结果
        """
        try:
            # 使用 PyMuPDF 将 PDF 转为图片
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            logger.info(f"[PARSER] PDF共 {total_pages} 页，开始逐页解析...")
            all_content = []

            async with httpx.AsyncClient(timeout=60.0) as client:
                for page_num in range(total_pages):
                    logger.info(f"[PARSER] 正在解析第 {page_num + 1}/{total_pages} 页...")
                    page = doc[page_num]

                    # 渲染为图片（2倍分辨率以获得更好效果）
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat)

                    # 转换为 PNG 字节
                    img_bytes = pix.tobytes("png")
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    logger.info(f"[PARSER]   页面图片大小: {len(img_bytes)} bytes")

                    # 调用 Qwen-VL API
                    logger.info(f"[PARSER]   调用Qwen-VL API...")
                    response = await client.post(
                        f"{DASHSCOPE_API_BASE}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "qwen-vl-plus",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "请将这张文档页面的内容提取为Markdown格式。保留标题层级、列表、表格等结构。只输出Markdown内容，不要添加额外说明。"
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/png;base64,{img_base64}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            "max_tokens": 4096
                        }
                    )

                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        if content:
                            all_content.append(f"## 第 {page_num + 1} 页\n\n{content}")
                            logger.info(f"[PARSER]   解析成功，内容长度: {len(content)} 字符")
                            # 显示内容预览
                            preview = content[:150].replace('\n', ' ')
                            logger.info(f"[PARSER]   内容预览: {preview}...")
                        else:
                            logger.warning(f"[PARSER]   解析结果为空")
                            all_content.append(f"## 第 {page_num + 1} 页\n\n[内容为空]")
                    else:
                        logger.warning(f"[PARSER]   Qwen-VL API失败: {response.status_code}")
                        logger.warning(f"[PARSER]   响应: {response.text[:200]}")
                        all_content.append(f"## 第 {page_num + 1} 页\n\n[解析失败]")

                    # 避免 API 限流
                    await asyncio.sleep(0.5)

            doc.close()
            final_content = "\n\n---\n\n".join(all_content)
            logger.info(f"[PARSER] Qwen-VL解析完成，总内容长度: {len(final_content)} 字符")
            return final_content

        except Exception as e:
            logger.error(f"[PARSER] Qwen-VL解析PDF失败: {e}", exc_info=True)
            return ""

    @classmethod
    async def _fallback_parse(cls, filename: str, content_bytes: bytes) -> str:
        """
        降级本地解析方案

        当 API 不可用时使用本地库解析
        """
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        logger.info(f"[PARSER] ----- 使用本地降级解析 -----")
        logger.info(f"[PARSER] 文件类型: {ext}")

        try:
            if ext == 'pdf':
                logger.info(f"[PARSER] 本地解析PDF...")
                result = cls._local_parse_pdf(content_bytes)
            elif ext == 'docx':
                logger.info(f"[PARSER] 本地解析DOCX...")
                result = cls._local_parse_docx(content_bytes)
            elif ext in ('ppt', 'pptx'):
                logger.info(f"[PARSER] 本地解析PPT/PPTX...")
                result = cls._local_parse_pptx(content_bytes)
            else:
                logger.info(f"[PARSER] 作为文本解析...")
                result = cls._parse_text(content_bytes)

            logger.info(f"[PARSER] 本地解析完成，内容长度: {len(result)} 字符")
            if result:
                preview = result[:200].replace('\n', ' ')
                logger.info(f"[PARSER] 内容预览: {preview}...")
            return result
        except Exception as e:
            logger.error(f"[PARSER] 本地解析失败 [{filename}]: {e}", exc_info=True)
            return ""

    @classmethod
    def _local_parse_pdf(cls, content_bytes: bytes) -> str:
        """本地解析 PDF"""
        try:
            pdf_reader = PdfReader(io.BytesIO(content_bytes))
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return '\n\n'.join(text_parts)
        except Exception as e:
            logger.error(f"本地 PDF 解析失败: {e}")
            return ""

    @classmethod
    def _local_parse_docx(cls, content_bytes: bytes) -> str:
        """本地解析 Word 文档"""
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(io.BytesIO(content_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return '\n\n'.join(paragraphs)
        except Exception as e:
            logger.error(f"本地 DOCX 解析失败: {e}")
            return ""

    @classmethod
    def _local_parse_pptx(cls, content_bytes: bytes) -> str:
        """本地解析 PPT 文档（仅提取文本）"""
        try:
            from pptx import Presentation
            prs = Presentation(io.BytesIO(content_bytes))
            all_text = []

            for slide_num, slide in enumerate(prs.slides, 1):
                slide_text = [f"## 第 {slide_num} 页"]
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text.append(shape.text.strip())
                all_text.append('\n\n'.join(slide_text))

            return '\n\n---\n\n'.join(all_text)
        except Exception as e:
            logger.error(f"本地 PPTX 解析失败: {e}")
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
        all_supported = cls.SUPPORTED_TEXT | cls.SUPPORTED_DOCX | cls.SUPPORTED_QWEN_VL | cls.SUPPORTED_PPT
        return ext in all_supported


# 便捷函数（异步版本）
async def parse_file_content(filename: str, content_bytes: bytes) -> str:
    """解析文件内容（便捷函数）"""
    return await FileParser.parse(filename, content_bytes)


# 同步包装器（兼容旧代码）
def parse_file_content_sync(filename: str, content_bytes: bytes) -> str:
    """解析文件内容（同步版本，用于兼容）"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果已经在异步上下文中，创建新任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    FileParser.parse(filename, content_bytes)
                )
                return future.result()
        else:
            return loop.run_until_complete(FileParser.parse(filename, content_bytes))
    except RuntimeError:
        return asyncio.run(FileParser.parse(filename, content_bytes))
