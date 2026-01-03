"""
RAG 聊天 API

使用双索引智能路由：
- 细节问题 -> Detail Index（原文分块）
- 全局问题 -> Summary Index（文档摘要）
"""
import re
import logging
from typing import Optional, List

from fastapi import APIRouter, Header
from langchain_core.messages import HumanMessage, SystemMessage

from ..models import ChatRequest, ChatResponse, SourceItem, IndexType
from ..dependencies import get_llm, get_hybrid_retriever, get_query_router, get_reranker

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


def _convert_minio_urls(text: str) -> str:
    """
    将文本中的 minio:// URL 转换为预签名 URL

    匹配格式：![description](minio://object_name)
    转换为：![description](https://presigned-url)

    Args:
        text: 包含 minio:// URL 的文本

    Returns:
        转换后的文本
    """
    if "minio://" not in text:
        return text

    try:
        from app.services.minio_service import get_minio_service
        minio_service = get_minio_service()
    except Exception as e:
        logger.warning(f"[CHAT] MinIO 服务不可用，无法转换图片 URL: {e}")
        return text

    # 匹配 ![...](minio://...) 格式
    pattern = r'!\[([^\]]*)\]\(minio://([^)]+)\)'

    def replace_url(match):
        alt_text = match.group(1)
        object_name = match.group(2)
        try:
            presigned_url = minio_service.get_presigned_url(object_name, expires=3600)
            logger.info(f"[CHAT] 转换图片 URL: minio://{object_name} -> presigned URL")
            return f"![{alt_text}]({presigned_url})"
        except Exception as e:
            logger.warning(f"[CHAT] 获取预签名 URL 失败 [{object_name}]: {e}")
            return match.group(0)  # 保持原样

    return re.sub(pattern, replace_url, text)

# 系统提示词模板
SYSTEM_PROMPT_WITH_SOURCES = """你是一个专业的学习助手。

回答要求：
1. 基于提供的资料回答问题
2. 在引用内容后添加角标 [1]、[2] 等
3. 回答要清晰、准确、有条理
4. 使用中文回答
5. 直接回答问题，不要以"根据资料"等开头
"""

SYSTEM_PROMPT_NO_SOURCES = """你是一个专业的学习助手。
使用中文回答用户的问题。"""

# 相关性分数阈值（向量检索初筛）：低于此分数的结果直接过滤
RELEVANCE_THRESHOLD = 0.35

# 重排序相关性阈值：使用 LLM 重排序后，低于此分数视为不相关
RERANK_THRESHOLD = 0.5


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    x_user_id: str = Header(..., alias="x-user-id"),
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """RAG 问答（双索引智能路由）"""
    logger.info(f"[CHAT] ========================================")
    logger.info(f"[CHAT] ========== 新的问答请求 ==========")
    logger.info(f"[CHAT] ========================================")
    logger.info(f"[CHAT] 用户ID: {x_user_id}")
    logger.info(f"[CHAT] 问题: {req.message}")
    logger.info(f"[CHAT] 知识库IDs: {req.knowledge_ids}")
    logger.info(f"[CHAT] 历史消息数: {len(req.history) if req.history else 0}")

    try:
        if not req.message.strip():
            return ChatResponse(success=False, error="请输入问题")

        llm = get_llm(x_api_key)
        retrieval_info = {}

        # 智能路由：分析查询类型，决定使用哪个索引
        query_router = get_query_router()
        query_type, index_type, retrieval_params = query_router.route(req.message)

        retrieval_info["query_type"] = query_type.value
        retrieval_info["index_type"] = index_type.value
        retrieval_info["retrieval_params"] = retrieval_params

        logger.info(f"[CHAT] 查询类型: {query_type.value}")
        logger.info(f"[CHAT] 索引类型: {index_type.value}")
        logger.info(f"[CHAT] 检索参数: {retrieval_params}")

        # 检索相关文档
        sources: List[SourceItem] = []

        if req.knowledge_ids:
            logger.info(f"[CHAT] 开始检索...")
            sources, raw_results = _retrieve_sources(
                req.message, req.knowledge_ids, index_type, retrieval_params, retrieval_info
            )

            # 向量检索初筛：过滤低相关性结果
            original_count = len(sources)
            sources = [s for s in sources if s.score >= RELEVANCE_THRESHOLD]
            filtered_count = original_count - len(sources)

            if filtered_count > 0:
                logger.info(f"[CHAT] 向量初筛: {original_count} -> {len(sources)} (阈值={RELEVANCE_THRESHOLD})")

            # 重排序：使用 Rerank 模型判断真实相关性
            if sources and raw_results:
                logger.info(f"[CHAT] 开始重排序...")
                reranker = get_reranker()
                # 只对通过初筛的文档进行重排序
                filtered_raw = [(doc, score) for doc, score in raw_results if score >= RELEVANCE_THRESHOLD]
                rerank_results = reranker.rerank(req.message, filtered_raw)

                # 重新构建 sources 列表，只保留重排序后相关的文档
                reranked_sources = []
                for result in rerank_results:
                    doc = result.document
                    content = doc.metadata.get("large_chunk", doc.page_content)
                    reranked_sources.append(SourceItem(
                        name=doc.metadata.get("name", "未知来源"),
                        content=content,
                        course_name=doc.metadata.get("course_name"),
                        score=round(result.rerank_score, 4)
                    ))

                logger.info(f"[CHAT] 重排序结果: {len(sources)} -> {len(reranked_sources)} 条相关资料")
                sources = reranked_sources

            logger.info(f"[CHAT] ========== 检索结果: {len(sources)} 条相关资料 ==========")
            for i, src in enumerate(sources):
                logger.info(f"[CHAT] ----- 资料 {i+1} -----")
                logger.info(f"[CHAT] 来源: {src.name}")
                logger.info(f"[CHAT] 课程: {src.course_name or '个人知识库'}")
                logger.info(f"[CHAT] 相关度: {src.score}")
                logger.info(f"[CHAT] 内容({len(src.content)}字):")
                # 显示更多内容，限制300字
                content_lines = src.content[:300].split('\n')
                for line in content_lines:
                    if line.strip():
                        logger.info(f"[CHAT]   {line}")
                if len(src.content) > 300:
                    logger.info(f"[CHAT]   ... (省略 {len(src.content) - 300} 字)")
        else:
            logger.info(f"[CHAT] 无知识库ID，跳过检索")

        # 构建提示词
        system_prompt, user_prompt = _build_prompts(req.message, req.history, sources)
        logger.info(f"[CHAT] 构建提示词完成")
        logger.info(f"[CHAT] 系统提示词长度: {len(system_prompt)} 字符")
        logger.info(f"[CHAT] 用户提示词长度: {len(user_prompt)} 字符")

        # 调用 LLM
        logger.info(f"[CHAT] 调用 LLM...")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)
        answer = response.content

        logger.info(f"[CHAT] ========== LLM 回答 ==========")
        logger.info(f"[CHAT] 回答长度: {len(answer)} 字符")
        logger.info(f"[CHAT] 完整回答内容:")
        # 按行显示完整回答
        answer_lines = answer.split('\n')
        for line in answer_lines:
            logger.info(f"[CHAT]   {line}")

        # 过滤未被引用的 sources（只保留回答中实际引用的）并重新映射编号
        answer, used_sources = _filter_used_sources(answer, sources)
        logger.info(f"[CHAT] 引用过滤: {len(sources)} -> {len(used_sources)} 个来源")

        # 转换 sources 中的 minio:// URL 为预签名 URL
        for source in used_sources:
            source.content = _convert_minio_urls(source.content)

        logger.info(f"[CHAT] ========== 问答请求结束 ==========")

        return ChatResponse(
            success=True,
            message=answer,
            sources=used_sources,
            retrieval_info=retrieval_info
        )

    except Exception as e:
        logger.error(f"[CHAT] 聊天请求失败: {e}", exc_info=True)
        return ChatResponse(success=False, error=str(e))


def _retrieve_sources(
    query: str,
    knowledge_ids: List[str],
    index_type: IndexType,
    retrieval_params: dict,
    retrieval_info: dict
) -> tuple[List[SourceItem], list]:
    """
    检索相关源数据

    Args:
        query: 用户问题
        knowledge_ids: 知识库ID列表
        index_type: 索引类型（DETAIL 或 SUMMARY）
        retrieval_params: 检索参数
        retrieval_info: 检索信息（用于调试）

    Returns:
        (源数据列表, 原始检索结果列表) - 原始结果用于重排序
    """
    sources = []

    # 使用混合检索器（支持双索引）
    hybrid_retriever = get_hybrid_retriever()
    results = hybrid_retriever.retrieve(
        query=query,
        knowledge_ids=knowledge_ids,
        index_type=index_type,
        top_k=retrieval_params["top_k"],
        vector_weight=retrieval_params["vector_weight"],
        bm25_weight=retrieval_params["bm25_weight"],
        use_large_chunk=retrieval_params.get("use_large_chunk", True)
    )

    retrieval_info["results_count"] = len(results)

    # 构建源数据
    seen_contents = set()
    for doc, score in results:
        # 根据索引类型获取内容
        if index_type == IndexType.SUMMARY:
            # 摘要索引：直接使用摘要内容
            content = doc.page_content
        else:
            # 原文索引：使用大块内容（如果有）
            if retrieval_params.get("use_large_chunk", True):
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

    return sources, results


def _filter_used_sources(answer: str, sources: List[SourceItem]) -> tuple[str, List[SourceItem]]:
    """
    过滤未被引用的来源，只保留 LLM 回答中实际引用的，并重新映射引用编号

    Args:
        answer: LLM 回答文本
        sources: 原始来源列表

    Returns:
        (重新编号后的回答, 被引用的来源列表)
    """
    import re

    if not sources:
        return answer, []

    # 提取回答中所有的引用编号，如 [1], [2], [3]
    pattern = r'\[(\d+)\]'
    matches = re.findall(pattern, answer)

    if not matches:
        # 如果没有引用标记，返回空列表（LLM 没有使用任何资料）
        logger.info(f"[CHAT] 回答中未找到引用标记，不返回来源")
        return answer, []

    # 获取被引用的索引（转为0-based），保持出现顺序
    cited_indices = []
    seen = set()
    for match in matches:
        try:
            idx = int(match) - 1  # 转为0-based索引
            if 0 <= idx < len(sources) and idx not in seen:
                cited_indices.append(idx)
                seen.add(idx)
        except ValueError:
            continue

    if not cited_indices:
        logger.info(f"[CHAT] 引用编号无效，不返回来源")
        return answer, []

    # 构建旧编号到新编号的映射
    # 例如：原来引用了 [2] 和 [5]，映射为 [1] 和 [2]
    old_to_new = {}
    for new_idx, old_idx in enumerate(sorted(cited_indices)):
        old_to_new[old_idx + 1] = new_idx + 1  # 转回1-based

    logger.info(f"[CHAT] 引用编号映射: {old_to_new}")

    # 替换回答中的引用编号
    def replace_citation(match):
        old_num = int(match.group(1))
        if old_num in old_to_new:
            return f"[{old_to_new[old_num]}]"
        return match.group(0)  # 保持不变

    updated_answer = re.sub(pattern, replace_citation, answer)

    # 按原始顺序返回被引用的来源
    used_sources = []
    for idx in sorted(cited_indices):
        used_sources.append(sources[idx])

    logger.info(f"[CHAT] 被引用的来源索引: {sorted(cited_indices)}")
    logger.info(f"[CHAT] 来源数量: {len(sources)} -> {len(used_sources)}")

    return updated_answer, used_sources


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
