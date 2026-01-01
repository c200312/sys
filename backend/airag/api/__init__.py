"""
API 路由模块
"""
from .knowledge import router as knowledge_router
from .chat import router as chat_router

__all__ = ["knowledge_router", "chat_router"]
