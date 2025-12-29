"""
AI Providers 模块

目前仅实现 Mock Provider，真实 AI 接口待后续开发。

使用方式：
    from app.providers import get_ai_provider

    provider = get_ai_provider()
    response = await provider.generate_ppt(request)
"""
from app.core.config import get_settings
from app.providers.base import AIProvider
from app.providers.mock import MockAIProvider

# 未来可以添加更多 Provider
# from app.providers.openai import OpenAIProvider
# from app.providers.claude import ClaudeProvider


def get_ai_provider() -> AIProvider:
    """
    获取 AI Provider 实例

    根据配置返回对应的 AI Provider
    """
    settings = get_settings()

    if settings.ai_provider == "mock":
        return MockAIProvider()
    # elif settings.ai_provider == "openai":
    #     return OpenAIProvider(api_key=settings.ai_api_key, model=settings.ai_model)
    # elif settings.ai_provider == "claude":
    #     return ClaudeProvider(api_key=settings.ai_api_key, model=settings.ai_model)
    else:
        # 默认返回 Mock Provider
        return MockAIProvider()


__all__ = [
    "AIProvider",
    "MockAIProvider",
    "get_ai_provider",
]
