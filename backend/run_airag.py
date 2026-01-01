"""启动 AI RAG 服务"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.airag.main import start

if __name__ == "__main__":
    start()
