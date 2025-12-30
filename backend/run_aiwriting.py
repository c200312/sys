#!/usr/bin/env python
"""
AI 写作服务启动脚本

用法:
    python run_aiwriting.py

服务将在 http://localhost:8003 启动
"""
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 切换工作目录到 aiwriting 模块
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiwriting"))

import uvicorn
from dotenv import load_dotenv

# 加载后端主目录的环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

if __name__ == "__main__":
    port = int(os.getenv("AIWRITING_PORT", 8003))
    print(f"🚀 Starting AI Writing Assistant on http://localhost:{port}")

    uvicorn.run(
        "aiwriting.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
