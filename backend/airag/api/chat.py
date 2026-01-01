"""
RAG 聊天 API
"""
import logging
from typing import Optional, List

from fastapi import APIRouter, Header
from langchain_core.messages import HumanMessage, SystemMessage

from ..models import ChatRequest, ChatResponse, SourceItem
from ..dependencies import get_llm, get_hybrid_retriever, get_query_router

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# 系统提示词模板
SYSTEM_PROMPT_WITH_SOURCES = """你是一个专业的学习助手，根据提供的知识库资料回答用户的问题。

回答要求：
1. 只基于提供的资料内容进行回答，不要编造信息
2. 如果资料中没有相关内容，诚实地告诉用户
3. 回答要清晰、准确、有条理
4. 【重要】在引用资料内容时，必须在相关内容后面添加角标标注来源，格式为 [1]、[2] 等
5. 可以同时引用多个来源，如 [1][2]
6. 使用中文回答

角标示例：
- "根据资料显示，该算法的时间复杂度为O(n)[1]。"
- "研究表明这种方法可以提高效率[2][3]。"
"""

SYSTEM_PROMPT_NO_SOURCES = """你是一个专业的学习助手，友好地回答用户的问题。
使用中文回答。如果问题需要特定的资料，建议用户添加相关知识库。"""


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    x_user_id: str = Header(..., alias="x-user-id"),
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """RAG 问答（使用混合检索 + 智能路由）"""
    logger.info(f"[RAG] 收到问题: {req.message[:50]}...")

    try:
        if not req.message.strip():
            return ChatResponse(success=False, error="请输入问题")

        llm = get_llm(x_api_key)
        retrieval_info = {}

        # 智能路由：分析查询类型
        query_router = get_query_router()
        query_type = query_router.classify_query(req.message)
        retrieval_params = query_router.get_retrieval_params(query_type)

        retrieval_info["query_type"] = query_type.value
        retrieval_info["retrieval_params"] = retrieval_params

        logger.info(f"[RAG] 查询类型: {query_type.value}, 参数: {retrieval_params}")

        # 检索相关文档
        sources: List[SourceItem] = []

        if req.knowledge_ids:
            sources = _retrieve_sources(req.message, req.knowledge_ids, retrieval_params, retrieval_info)

        # 构建提示词
        system_prompt, user_prompt = _build_prompts(req.message, req.history, sources)

        # 调用 LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)

        logger.info(f"[RAG] 回答完成，sources={len(sources)}")

        return ChatResponse(
            success=True,
            message=response.content,
            sources=sources,
            retrieval_info=retrieval_info
        )

    except Exception as e:
        logger.error(f"聊天请求失败: {e}", exc_info=True)
        return ChatResponse(success=False, error=str(e))


def _retrieve_sources(
    query: str,
    knowledge_ids: List[str],
    retrieval_params: dict,
    retrieval_info: dict
) -> List[SourceItem]:
    """检索相关源数据"""
    sources = []

    # 使用混合检索
    hybrid_retriever = get_hybrid_retriever()
    results = hybrid_retriever.retrieve(
        query=query,
        knowledge_ids=knowledge_ids,
        top_k=retrieval_params["top_k"],
        vector_weight=retrieval_params["vector_weight"],
        bm25_weight=retrieval_params["bm25_weight"]
    )

    retrieval_info["results_count"] = len(results)

    # 构建源数据（使用大块内容）
    seen_contents = set()
    for doc, score in results:
        # 使用大块内容（如果有）
        if retrieval_params["use_large_chunk"]:
            content = doc.metadata.get("large_chunk", doc.page_content)
        else:
            content = doc.page_content

        content_key = (doc.metadata.get("name", "未知"), content[:100])
        if content_key not in seen_contents:
            seen_contents.add(content_key)
            sources.append(SourceItem(
                name=doc.metadata.get("name", "未知来源"),
                content=content,
                course_name=doc.metadata.get("course_name"),
                score=round(score, 4)
            ))

    return sources


def _build_prompts(
    message: str,
    history: List[dict],
    sources: List[SourceItem]
) -> tuple[str, str]:
    """构建系统提示和用户提示"""
    # 构建历史消息
    history_text = ""
    if history:
        history_parts = []
        for msg in history[-6:]:
            role = "用户" if msg.get("role") == "user" else "助手"
            history_parts.append(f"{role}: {msg.get('content', '')}")
        history_text = "\n".join(history_parts)

    if sources:
        # 构建带编号的资料上下文
        context_parts = []
        for i, source in enumerate(sources):
            context_parts.append(f"[资料{i + 1}] 来源：{source.name}\n{source.content}")

        context = "\n\n---\n\n".join(context_parts)

        system_prompt = SYSTEM_PROMPT_WITH_SOURCES

        user_prompt = f"""【知识库资料】
{context}

"""
        if history_text:
            user_prompt += f"""【对话历史】
{history_text}

"""
        user_prompt += f"""【用户问题】
{message}

请根据以上知识库资料回答用户的问题。"""
    else:
        system_prompt = SYSTEM_PROMPT_NO_SOURCES

        user_prompt = ""
        if history_text:
            user_prompt += f"【对话历史】\n{history_text}\n\n"
        user_prompt += f"【用户问题】\n{message}"

    return system_prompt, user_prompt
