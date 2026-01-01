"""
智能查询路由器：双索引路由策略

基于 LlamaIndex 的 RouterQueryEngine 思想：
- 细节问题 -> Detail Index（原文分块索引）
- 全局问题 -> Summary Index（文档摘要索引）
"""
import logging
from typing import Dict, Any

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .models import QueryType, IndexType

logger = logging.getLogger(__name__)


class RouteDecision(BaseModel):
    """路由决策结果"""
    index_type: str = Field(
        description="选择的索引类型: DETAIL(细节问题，查原文) 或 GLOBAL(全局问题，查摘要)"
    )
    confidence: float = Field(
        description="置信度，0-1之间",
        ge=0,
        le=1
    )
    reasoning: str = Field(
        description="路由决策的理由"
    )


class QueryRouter:
    """
    智能查询路由器 - 双索引路由

    根据问题类型选择不同的检索索引：
    - DETAIL（细节问题）：
      - 询问具体细节、定义、数据、代码片段
      - 需要精确匹配原文
      - 例如："这个函数的参数是什么？"、"第三章讲了什么？"

    - GLOBAL（全局问题）：
      - 询问文档主旨、总结、概述
      - 需要理解整体内容
      - 例如："这篇文章主要讲什么？"、"总结一下核心观点"
    """

    # 路由选项定义
    ROUTE_CHOICES = {
        "DETAIL": {
            "name": "DETAIL",
            "index_type": IndexType.DETAIL,
            "query_type": QueryType.DETAIL,
            "description": "细节问题：询问具体内容、定义、数据、步骤、代码、某一部分的详细信息。需要从原文中精确检索。",
            "examples": [
                "这个函数怎么用？",
                "第三章讲了什么内容？",
                "机器学习的定义是什么？",
                "这段代码是做什么的？",
                "具体步骤是什么？",
            ],
            "retrieval_params": {
                "top_k": 5,
                "vector_weight": 0.7,
                "bm25_weight": 0.3,
                "use_large_chunk": True,
            }
        },
        "GLOBAL": {
            "name": "GLOBAL",
            "index_type": IndexType.SUMMARY,
            "query_type": QueryType.GLOBAL,
            "description": "全局问题：询问文档主旨、总结、概述、核心观点、整体结构。需要从文档摘要中检索。",
            "examples": [
                "这篇文章主要讲什么？",
                "总结一下核心内容",
                "这个课程的主题是什么？",
                "文档的整体结构是怎样的？",
                "概括一下主要观点",
            ],
            "retrieval_params": {
                "top_k": 3,
                "vector_weight": 0.9,
                "bm25_weight": 0.1,
                "use_large_chunk": False,  # 摘要本身就是完整的
            }
        }
    }

    def __init__(self, llm):
        """
        初始化路由器

        Args:
            llm: LangChain LLM 实例
        """
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=RouteDecision)
        self._setup_prompt()

    def _setup_prompt(self):
        """设置路由选择提示词"""
        # 构建路由选项描述
        choices_text = ""
        for key, choice in self.ROUTE_CHOICES.items():
            examples = "\n      - ".join(choice["examples"])
            choices_text += f"""
{key}: {choice["description"]}
    示例问题：
      - {examples}
"""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能查询路由器。你的任务是判断用户问题应该使用哪个索引来检索。

有两种索引类型：
{choices}

请根据用户问题的意图，选择最合适的索引类型。

判断规则：
1. 如果问题是关于具体细节、特定内容、定义、步骤、代码等，选择 DETAIL
2. 如果问题是关于总结、概述、主旨、核心观点、整体理解等，选择 GLOBAL
3. 如果不确定，默认选择 DETAIL（因为细节问题更常见）

{format_instructions}"""),
            ("human", "用户问题：{query}")
        ])

        self.choices_text = choices_text

    def route(self, query: str) -> tuple[QueryType, IndexType, Dict[str, Any]]:
        """
        路由查询：决定使用哪个索引

        Args:
            query: 用户查询文本

        Returns:
            (查询类型, 索引类型, 检索参数) 三元组
        """
        logger.info(f"[ROUTER] ========== 开始智能路由 ==========")
        logger.info(f"[ROUTER] 查询内容: {query}")

        try:
            # 构建消息
            messages = self.prompt.format_messages(
                choices=self.choices_text,
                format_instructions=self.parser.get_format_instructions(),
                query=query
            )

            # 调用 LLM
            response = self.llm.invoke(messages)
            result_text = response.content.strip()

            logger.info(f"[ROUTER] LLM 原始返回: {result_text[:300]}...")

            # 解析结果
            try:
                decision = self.parser.parse(result_text)
                index_type_str = decision.index_type.upper()

                logger.info(f"[ROUTER] 解析结果:")
                logger.info(f"[ROUTER]   索引类型: {index_type_str}")
                logger.info(f"[ROUTER]   置信度: {decision.confidence:.2f}")
                logger.info(f"[ROUTER]   理由: {decision.reasoning}")

                if index_type_str in self.ROUTE_CHOICES:
                    choice = self.ROUTE_CHOICES[index_type_str]
                    logger.info(f"[ROUTER] ========== 路由结束 ==========")
                    return (
                        choice["query_type"],
                        choice["index_type"],
                        choice["retrieval_params"]
                    )

            except Exception as parse_error:
                logger.warning(f"[ROUTER] 解析失败，尝试简单匹配: {parse_error}")
                # 降级：尝试从返回内容中提取类型
                result_upper = result_text.upper()
                if "GLOBAL" in result_upper or "摘要" in result_text or "总结" in result_text:
                    logger.info(f"[ROUTER] 简单匹配结果: GLOBAL")
                    choice = self.ROUTE_CHOICES["GLOBAL"]
                    return (
                        choice["query_type"],
                        choice["index_type"],
                        choice["retrieval_params"]
                    )

            # 默认使用 DETAIL
            logger.warning(f"[ROUTER] 无法识别类型，使用默认值: DETAIL")
            choice = self.ROUTE_CHOICES["DETAIL"]
            logger.info(f"[ROUTER] ========== 路由结束 ==========")
            return (
                choice["query_type"],
                choice["index_type"],
                choice["retrieval_params"]
            )

        except Exception as e:
            logger.error(f"[ROUTER] LLM 路由失败: {e}", exc_info=True)
            choice = self.ROUTE_CHOICES["DETAIL"]
            return (
                choice["query_type"],
                choice["index_type"],
                choice["retrieval_params"]
            )

    def classify_query(self, query: str) -> QueryType:
        """
        分类查询（兼容旧接口）

        Args:
            query: 用户查询文本

        Returns:
            查询类型枚举
        """
        query_type, _, _ = self.route(query)
        return query_type

    def get_retrieval_params(self, query_type: QueryType) -> Dict[str, Any]:
        """
        获取检索参数（兼容旧接口）

        Args:
            query_type: 查询类型

        Returns:
            检索参数字典
        """
        for choice in self.ROUTE_CHOICES.values():
            if choice["query_type"] == query_type:
                return choice["retrieval_params"]

        # 默认参数
        return self.ROUTE_CHOICES["DETAIL"]["retrieval_params"]

    def get_route_choices(self) -> Dict[str, Any]:
        """
        获取所有路由选项（用于调试/展示）

        Returns:
            路由选项字典
        """
        return {
            key: {
                "name": choice["name"],
                "description": choice["description"],
                "examples": choice["examples"],
                "retrieval_params": choice["retrieval_params"]
            }
            for key, choice in self.ROUTE_CHOICES.items()
        }
