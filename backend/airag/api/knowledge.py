"""
知识库管理 API

双索引策略：
- Detail Index: 原文分块索引
- Summary Index: 文档摘要索引
"""
import uuid
import base64
import logging
from typing import Optional, Dict, List
from datetime import datetime

from fastapi import APIRouter, Header, UploadFile, File, Form
from langchain_core.documents import Document as LCDocument

from ..models import (
    AddKnowledgeRequest,
    ListKnowledgeRequest,
    KnowledgeSourceType,
)
from ..parser import parse_file_content
from ..dependencies import (
    get_detail_chroma,
    get_summary_chroma,
    get_chunker,
    get_summarizer,
    rebuild_bm25_index
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


async def _add_to_indexes(
    knowledge_id: str,
    text_content: str,
    metadata: dict,
    filename: str
) -> int:
    """
    添加文档到双索引

    Args:
        knowledge_id: 知识库ID
        text_content: 文档文本内容
        metadata: 元数据
        filename: 文件名

    Returns:
        分块数量
    """
    # 1. 原文分块 -> Detail Index
    logger.info(f"[KNOWLEDGE] ----- 构建原文索引 -----")
    chunker = get_chunker()
    chunks = chunker.create_hierarchical_chunks(text_content, metadata)

    if not chunks:
        raise ValueError("文档分割失败")

    logger.info(f"[KNOWLEDGE] 分块完成，共 {len(chunks)} 个块")

    # 创建原文文档
    detail_documents = []
    for chunk in chunks:
        doc = LCDocument(
            page_content=chunk.small_chunk,
            metadata={
                **chunk.metadata,
                "large_chunk": chunk.large_chunk,
                "chunk_id": chunk.chunk_id,
            }
        )
        detail_documents.append(doc)

    # 添加到 Detail Index
    detail_chroma = get_detail_chroma()
    ids = [chunk.chunk_id for chunk in chunks]
    detail_chroma.add_documents(documents=detail_documents, ids=ids)
    logger.info(f"[KNOWLEDGE] 原文索引添加成功: {len(detail_documents)} 个块")

    # 2. 生成块级摘要 -> Summary Index
    logger.info(f"[KNOWLEDGE] ----- 构建摘要索引 -----")
    summarizer = get_summarizer()
    chunk_summaries = summarizer.generate_chunk_summaries(text_content, filename)

    # 创建摘要文档列表（每个块摘要一条记录）
    summary_documents = []
    summary_ids = []
    for cs in chunk_summaries:
        summary_doc = LCDocument(
            page_content=cs.summary,  # 块摘要用于检索
            metadata={
                "knowledge_id": knowledge_id,
                "name": metadata.get("name"),
                "source_type": metadata.get("source_type"),
                "owner_id": metadata.get("owner_id"),
                "course_id": metadata.get("course_id"),
                "course_name": metadata.get("course_name"),
                "created_at": metadata.get("created_at"),
                "doc_type": "summary",
                "chunk_index": cs.chunk_index,
                "original_chunk": cs.original_chunk,  # 原始块内容用于引用展示
            }
        )
        summary_documents.append(summary_doc)
        summary_ids.append(f"{knowledge_id}_summary_{cs.chunk_index}")

    # 添加到 Summary Index
    summary_chroma = get_summary_chroma()
    summary_chroma.add_documents(documents=summary_documents, ids=summary_ids)
    logger.info(f"[KNOWLEDGE] 摘要索引添加成功: {len(summary_documents)} 个块摘要")
    for i, cs in enumerate(chunk_summaries[:3]):  # 预览前3个
        logger.info(f"[KNOWLEDGE]   块{i} 摘要: {cs.summary[:100]}...")

    # 3. 重建 BM25 索引
    logger.info(f"[KNOWLEDGE] 重建 BM25 索引...")
    rebuild_bm25_index()
    logger.info(f"[KNOWLEDGE] BM25 索引重建完成")

    return len(chunks)


@router.post("/add")
async def add_knowledge(
    req: AddKnowledgeRequest,
    x_user_id: str = Header(..., alias="x-user-id"),
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """添加资源到知识库（双索引策略）"""
    logger.info(f"[KNOWLEDGE] ========================================")
    logger.info(f"[KNOWLEDGE] ========== 添加个人知识库 ==========")
    logger.info(f"[KNOWLEDGE] ========================================")
    logger.info(f"[KNOWLEDGE] 文件名: {req.name}")
    logger.info(f"[KNOWLEDGE] 用户ID: {x_user_id}")
    logger.info(f"[KNOWLEDGE] 来源类型: {req.source_type}")

    try:
        # 解码文件内容
        if ',' in req.content_base64:
            content_base64 = req.content_base64.split(',')[1]
        else:
            content_base64 = req.content_base64

        content_bytes = base64.b64decode(content_base64)
        logger.info(f"[KNOWLEDGE] 文件大小: {len(content_bytes)} bytes")

        # 解析文件
        logger.info(f"[KNOWLEDGE] 开始解析文件...")
        text_content = await parse_file_content(req.name, content_bytes)

        if not text_content.strip():
            logger.error(f"[KNOWLEDGE] 解析结果为空")
            return {"success": False, "error": "无法解析文件内容"}

        logger.info(f"[KNOWLEDGE] 解析完成，内容长度: {len(text_content)} 字符")
        logger.info(f"[KNOWLEDGE] ----- 解析内容预览(前500字) -----")
        preview_lines = text_content[:500].split('\n')
        for line in preview_lines:
            if line.strip():
                logger.info(f"[KNOWLEDGE]   {line}")
        if len(text_content) > 500:
            logger.info(f"[KNOWLEDGE]   ... (省略 {len(text_content) - 500} 字)")

        # 生成知识库ID
        knowledge_id = str(uuid.uuid4())
        logger.info(f"[KNOWLEDGE] 知识库ID: {knowledge_id}")

        # 构建元数据
        metadata = {
            "knowledge_id": knowledge_id,
            "name": req.name,
            "source_type": req.source_type,
            "owner_id": x_user_id,
            "created_at": datetime.now().isoformat(),
        }
        if req.course_id:
            metadata["course_id"] = req.course_id

        # 添加到双索引
        chunks_count = await _add_to_indexes(
            knowledge_id, text_content, metadata, req.name
        )

        logger.info(f"[KNOWLEDGE] ========== 添加完成 ==========")
        logger.info(f"[KNOWLEDGE] 知识库: {req.name}")
        logger.info(f"[KNOWLEDGE] 分块数: {chunks_count}")

        return {
            "success": True,
            "knowledge_id": knowledge_id,
            "name": req.name,
            "chunks_count": chunks_count
        }

    except Exception as e:
        logger.error(f"[KNOWLEDGE] 添加失败: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.post("/add-from-course")
async def add_course_resource_to_knowledge(
    course_id: str = Form(...),
    course_name: str = Form(...),
    file_id: str = Form(...),
    file_name: str = Form(...),
    file_content: UploadFile = File(...),
    x_user_id: str = Header(..., alias="x-user-id"),
):
    """从课程资源添加到知识库（双索引策略）"""
    logger.info(f"[KNOWLEDGE] ========================================")
    logger.info(f"[KNOWLEDGE] ========== 添加课程资源 ==========")
    logger.info(f"[KNOWLEDGE] ========================================")
    logger.info(f"[KNOWLEDGE] 文件名: {file_name}")
    logger.info(f"[KNOWLEDGE] 课程ID: {course_id}")
    logger.info(f"[KNOWLEDGE] 课程名: {course_name}")
    logger.info(f"[KNOWLEDGE] 文件ID: {file_id}")
    logger.info(f"[KNOWLEDGE] 用户ID: {x_user_id}")

    try:
        content_bytes = await file_content.read()
        logger.info(f"[KNOWLEDGE] 文件大小: {len(content_bytes)} bytes")

        # 解析文件
        logger.info(f"[KNOWLEDGE] 开始解析文件...")
        text_content = await parse_file_content(file_name, content_bytes)

        if not text_content.strip():
            logger.error(f"[KNOWLEDGE] 解析结果为空")
            return {"success": False, "error": "无法解析文件内容"}

        logger.info(f"[KNOWLEDGE] 解析完成，内容长度: {len(text_content)} 字符")
        logger.info(f"[KNOWLEDGE] ----- 解析内容预览(前500字) -----")
        preview_lines = text_content[:500].split('\n')
        for line in preview_lines:
            if line.strip():
                logger.info(f"[KNOWLEDGE]   {line}")
        if len(text_content) > 500:
            logger.info(f"[KNOWLEDGE]   ... (省略 {len(text_content) - 500} 字)")

        knowledge_id = f"course_{course_id}_{file_id}"
        logger.info(f"[KNOWLEDGE] 知识库ID: {knowledge_id}")

        # 检查是否已存在（检查原文索引）
        detail_chroma = get_detail_chroma()
        existing = detail_chroma.get(where={"knowledge_id": knowledge_id})
        if existing and existing.get("ids"):
            logger.info(f"[KNOWLEDGE] 该资源已存在，跳过添加")
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "name": file_name,
                "message": "该资源已在知识库中"
            }

        # 构建元数据
        metadata = {
            "knowledge_id": knowledge_id,
            "name": file_name,
            "source_type": KnowledgeSourceType.COURSE,
            "owner_id": "system",
            "course_id": course_id,
            "course_name": course_name,
            "created_at": datetime.now().isoformat(),
        }

        # 添加到双索引
        chunks_count = await _add_to_indexes(
            knowledge_id, text_content, metadata, file_name
        )

        logger.info(f"[KNOWLEDGE] ========== 添加完成 ==========")
        logger.info(f"[KNOWLEDGE] 知识库: {file_name}")
        logger.info(f"[KNOWLEDGE] 分块数: {chunks_count}")

        return {
            "success": True,
            "knowledge_id": knowledge_id,
            "name": file_name,
            "chunks_count": chunks_count
        }

    except Exception as e:
        logger.error(f"[KNOWLEDGE] 添加课程资源失败: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.post("/list")
async def list_knowledge(
    req: ListKnowledgeRequest,
    x_user_id: str = Header(..., alias="x-user-id"),
):
    """获取用户可见的知识库列表"""
    try:
        detail_chroma = get_detail_chroma()
        all_data = detail_chroma.get(include=["metadatas"])

        if not all_data or not all_data.get("metadatas"):
            return {"success": True, "knowledge_list": []}

        knowledge_map: Dict[str, Dict] = {}

        for metadata in all_data["metadatas"]:
            kid = metadata.get("knowledge_id")
            if not kid:
                continue

            source_type = metadata.get("source_type")
            owner_id = metadata.get("owner_id")
            course_id = metadata.get("course_id")

            # 权限检查
            visible = False
            if source_type == KnowledgeSourceType.PERSONAL and owner_id == x_user_id:
                visible = True
            elif source_type == KnowledgeSourceType.COURSE and course_id in req.course_ids:
                visible = True

            if not visible:
                continue

            if kid not in knowledge_map:
                knowledge_map[kid] = {
                    "id": kid,
                    "name": metadata.get("name", "未知"),
                    "source_type": source_type,
                    "course_id": course_id,
                    "course_name": metadata.get("course_name"),
                    "owner_id": owner_id,
                    "created_at": metadata.get("created_at", ""),
                    "chunks_count": 0
                }
            knowledge_map[kid]["chunks_count"] += 1

        knowledge_list = list(knowledge_map.values())
        knowledge_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return {"success": True, "knowledge_list": knowledge_list}

    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}", exc_info=True)
        return {"success": False, "error": str(e), "knowledge_list": []}


@router.delete("/{knowledge_id:path}")
async def delete_knowledge(
    knowledge_id: str,
    x_user_id: str = Header(..., alias="x-user-id"),
):
    """删除知识库资源（从双索引中删除）"""
    try:
        detail_chroma = get_detail_chroma()
        summary_chroma = get_summary_chroma()

        # 检查原文索引
        existing = detail_chroma.get(where={"knowledge_id": knowledge_id}, include=["metadatas"])
        if not existing or not existing.get("ids"):
            return {"success": True, "message": "资源不存在"}

        metadata = existing["metadatas"][0]
        source_type = metadata.get("source_type")
        owner_id = metadata.get("owner_id")

        if source_type == KnowledgeSourceType.COURSE:
            if x_user_id != "system":
                return {"success": False, "error": "课程资源不可删除"}
        elif source_type == KnowledgeSourceType.PERSONAL:
            if owner_id != x_user_id:
                return {"success": False, "error": "无权删除此资源"}

        # 删除原文索引
        ids_to_delete = existing.get("ids", [])
        if ids_to_delete:
            detail_chroma.delete(ids=ids_to_delete)
            logger.info(f"[KNOWLEDGE] 已删除原文索引: {len(ids_to_delete)} 个块")

        # 删除摘要索引（可能有多个块摘要）
        try:
            summary_existing = summary_chroma.get(where={"knowledge_id": knowledge_id})
            if summary_existing and summary_existing.get("ids"):
                summary_chroma.delete(ids=summary_existing["ids"])
                logger.info(f"[KNOWLEDGE] 已删除摘要索引: {len(summary_existing['ids'])} 个块摘要")
        except Exception as e:
            logger.warning(f"[KNOWLEDGE] 删除摘要索引失败: {e}")

        # 重建 BM25 索引
        rebuild_bm25_index()

        logger.info(f"[KNOWLEDGE] 已删除知识库资源: {knowledge_id}")
        return {"success": True}

    except Exception as e:
        logger.error(f"删除失败: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/stats")
async def get_knowledge_stats(
    x_user_id: str = Header(..., alias="x-user-id"),
):
    """获取知识库统计信息"""
    try:
        detail_chroma = get_detail_chroma()
        summary_chroma = get_summary_chroma()

        detail_data = detail_chroma.get(include=["metadatas"])
        summary_data = summary_chroma.get(include=["metadatas"])

        total_detail_docs = len(detail_data.get("ids", []))
        total_summary_docs = len(summary_data.get("ids", []))
        knowledge_ids = set()

        for metadata in detail_data.get("metadatas", []):
            kid = metadata.get("knowledge_id")
            if kid:
                knowledge_ids.add(kid)

        from ..retriever import HAS_BM25

        return {
            "success": True,
            "total_detail_docs": total_detail_docs,
            "total_summary_docs": total_summary_docs,
            "total_knowledge": len(knowledge_ids),
            "bm25_enabled": HAS_BM25,
            "version": "4.0.0",
            "index_strategy": "dual_index"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
