#!/usr/bin/env python
"""
AI PPT Agent 服务启动脚本

用法:
    python run_aippt.py

服务将在 http://localhost:8002 启动
"""
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 切换工作目录到 aippt 模块
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "aippt"))

import uvicorn
from dotenv import load_dotenv

# 加载后端主目录的环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

if __name__ == "__main__":
    port = int(os.getenv("AIPPT_PORT", 8002))
    print(f"🚀 Starting AI PPT Agent on http://localhost:{port}")
    print(f"📁 Storage directory: {os.path.join(os.path.dirname(__file__), 'aippt', 'storage')}")

    uvicorn.run(
        "aippt.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
