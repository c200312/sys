"""
AI RAG 问答服务入口

使用 LlamaIndex 实现高级 RAG 问答：
- 混合检索：向量检索 + BM25 关键词检索
- 小索引大窗口：小块精确匹配，大块上下文返回
- 智能路由：根据问题类型优化检索参数
"""
import os

# 必须在导入任何库之前设置环境变量
os.environ["PYDANTIC_V2_MODE"] = "1"
os.environ["ANONYMIZED_TELEMETRY"] = "False"  # 禁用 ChromaDB 遥测

import logging
import sys

# 禁用 ChromaDB posthog 遥测的错误日志
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

# 配置日志（强制 UTF-8 编码）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

# 设置 stdout 编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

# 降低第三方库日志级别
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("llama_index").setLevel(logging.WARNING)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# 导入路由
from .api import knowledge_router, chat_router

# 创建应用
app = FastAPI(
    title="AI RAG Assistant",
    version="3.0.0",
    description="基于知识库的智能问答服务"
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(knowledge_router)
app.include_router(chat_router)


@app.get("/")
def health_check():
    """健康检查"""
    return {
        "status": "running",
        "service": "AI RAG Assistant",
        "version": "3.0.0"
    }


def start():
    """启动服务"""
    port = int(os.getenv("AIRAG_PORT", 8004))
    print(f"🚀 Starting AI RAG Assistant v3.0 on http://localhost:{port}")
    uvicorn.run("backend.airag.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    start()
