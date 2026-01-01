"""
知识库管理 API
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
from ..dependencies import get_chroma, get_chunker, rebuild_bm25_index

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/add")
async def add_knowledge(
    req: AddKnowledgeRequest,
    x_user_id: str = Header(..., alias="x-user-id"),
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """添加资源到知识库（使用层级分块）"""
    try:
        # 解码文件内容
        if ',' in req.content_base64:
            content_base64 = req.content_base64.split(',')[1]
        else:
            content_base64 = req.content_base64

        content_bytes = base64.b64decode(content_base64)
        text_content = parse_file_content(req.name, content_bytes)

        if not text_content.strip():
            return {"success": False, "error": "无法解析文件内容"}

        # 生成知识库ID
        knowledge_id = str(uuid.uuid4())

        # 使用层级分块器
        chunker = get_chunker()
        metadata = {
            "knowledge_id": knowledge_id,
            "name": req.name,
            "source_type": req.source_type,
            "owner_id": x_user_id,
            "created_at": datetime.now().isoformat(),
        }
        if req.course_id:
            metadata["course_id"] = req.course_id

        chunks = chunker.create_hierarchical_chunks(text_content, metadata)

        if not chunks:
            return {"success": False, "error": "文档分割失败"}

        # 创建文档（使用小块索引，存储大块内容）
        documents = []
        for chunk in chunks:
            doc = LCDocument(
                page_content=chunk.small_chunk,  # 小块用于索引
                metadata={
                    **chunk.metadata,
                    "large_chunk": chunk.large_chunk,  # 大块存储在元数据中
                    "chunk_id": chunk.chunk_id,
                }
            )
            documents.append(doc)

        # 添加到 ChromaDB
        chroma = get_chroma()
        ids = [chunk.chunk_id for chunk in chunks]
        chroma.add_documents(documents=documents, ids=ids)

        # 重建 BM25 索引
        rebuild_bm25_index()

        logger.info(f"[RAG] 已添加知识: {req.name} ({len(documents)} chunks) by user {x_user_id}")

        return {
            "success": True,
            "knowledge_id": knowledge_id,
            "name": req.name,
            "chunks_count": len(documents)
        }

    except Exception as e:
        logger.error(f"Add knowledge error: {e}", exc_info=True)
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
    """从课程资源添加到知识库"""
    logger.info(f"[RAG] 添加课程资源: {file_name}")

    try:
        content_bytes = await file_content.read()
        text_content = parse_file_content(file_name, content_bytes)

        if not text_content.strip():
            return {"success": False, "error": "无法解析文件内容"}

        knowledge_id = f"course_{course_id}_{file_id}"

        # 检查是否已存在
        chroma = get_chroma()
        existing = chroma.get(where={"knowledge_id": knowledge_id})
        if existing and existing.get("ids"):
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "name": file_name,
                "message": "该资源已在知识库中"
            }

        # 使用层级分块
        chunker = get_chunker()
        metadata = {
            "knowledge_id": knowledge_id,
            "name": file_name,
            "source_type": KnowledgeSourceType.COURSE,
            "owner_id": "system",
            "course_id": course_id,
            "course_name": course_name,
            "created_at": datetime.now().isoformat(),
        }

        chunks = chunker.create_hierarchical_chunks(text_content, metadata)

        if not chunks:
            return {"success": False, "error": "文档分割失败"}

        documents = []
        for chunk in chunks:
            doc = LCDocument(
                page_content=chunk.small_chunk,
                metadata={
                    **chunk.metadata,
                    "large_chunk": chunk.large_chunk,
                    "chunk_id": chunk.chunk_id,
                }
            )
            documents.append(doc)

        ids = [chunk.chunk_id for chunk in chunks]
        chroma.add_documents(documents=documents, ids=ids)

        # 重建 BM25 索引
        rebuild_bm25_index()

        logger.info(f"[RAG] 已添加课程资源: {file_name}, chunks={len(documents)}")

        return {
            "success": True,
            "knowledge_id": knowledge_id,
            "name": file_name,
            "chunks_count": len(documents)
        }

    except Exception as e:
        logger.error(f"添加课程资源失败: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.post("/list")
async def list_knowledge(
    req: ListKnowledgeRequest,
    x_user_id: str = Header(..., alias="x-user-id"),
):
    """获取用户可见的知识库列表"""
    try:
        chroma = get_chroma()
        all_data = chroma.get(include=["metadatas"])

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
    """删除知识库资源"""
    try:
        chroma = get_chroma()

        existing = chroma.get(where={"knowledge_id": knowledge_id}, include=["metadatas"])
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

        ids_to_delete = existing.get("ids", [])
        if ids_to_delete:
            chroma.delete(ids=ids_to_delete)
            # 重建 BM25 索引
            rebuild_bm25_index()

        logger.info(f"[RAG] 已删除知识库资源: {knowledge_id}")
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
        chroma = get_chroma()
        all_data = chroma.get(include=["metadatas"])

        total_docs = len(all_data.get("ids", []))
        knowledge_ids = set()

        for metadata in all_data.get("metadatas", []):
            kid = metadata.get("knowledge_id")
            if kid:
                knowledge_ids.add(kid)

        from ..retriever import HAS_BM25

        return {
            "success": True,
            "total_documents": total_docs,
            "total_knowledge": len(knowledge_ids),
            "bm25_enabled": HAS_BM25,
            "version": "3.0.0"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
