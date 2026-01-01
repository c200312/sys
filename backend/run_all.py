#!/usr/bin/env python
"""
统一服务启动脚本

同时启动主服务、AI PPT 服务、AI 写作服务、AI RAG 服务，支持热重载

用法:
    python run_all.py
"""
import os
import sys
import subprocess
import signal
import time
import atexit
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取当前目录
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# 服务配置
SERVICES = [
    {
        "name": "Main API",
        "port": int(os.getenv("PORT", 8080)),
        "module": "app.main:app",
    },
    {
        "name": "AI PPT",
        "port": int(os.getenv("AIPPT_PORT", 8002)),
        "module": "aippt.main:app",
    },
    {
        "name": "AI Writing",
        "port": int(os.getenv("AIWRITING_PORT", 8003)),
        "module": "aiwriting.main:app",
    },
    {
        "name": "AI RAG",
        "port": int(os.getenv("AIRAG_PORT", 8004)),
        "module": "airag.main:app",
    },
]

processes = []
stopping = False


def kill_port(port):
    """强制释放端口"""
    if sys.platform == "win32":
        try:
            # 查找占用端口的进程
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                check=False
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    pid = parts[-1]
                    if pid.isdigit():
                        subprocess.run(
                            ["taskkill", "/F", "/PID", pid],
                            capture_output=True,
                            check=False
                        )
        except Exception:
            pass


def kill_process_tree(pid):
    """杀死进程树（Windows）"""
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True,
                check=False,
                timeout=5
            )
        except Exception:
            pass
    else:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except Exception:
            try:
                os.kill(pid, signal.SIGTERM)
            except Exception:
                pass


def stop_all():
    """停止所有服务"""
    global stopping
    if stopping:
        return
    stopping = True

    print("\n" + "=" * 60)
    print("Stopping all services...")

    # 先尝试优雅关闭
    for proc in processes:
        if proc and proc.poll() is None:
            try:
                kill_process_tree(proc.pid)
            except Exception:
                pass

    # 等待进程结束
    time.sleep(1)

    # 强制杀死残留进程
    for proc in processes:
        if proc and proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass

    # 确保端口被释放
    for service in SERVICES:
        kill_port(service["port"])

    print("All services stopped")
    print("=" * 60)


def start_service(service):
    """启动单个服务"""
    port = service["port"]

    # 先确保端口空闲
    kill_port(port)
    time.sleep(0.3)

    # 确定热重载目录（包含模块根目录，uvicorn 会递归监听子目录）
    module_name = service["module"].split(":")[0].split(".")[0]
    reload_dir = os.path.join(BACKEND_DIR, module_name)

    cmd = [
        sys.executable, "-m", "uvicorn",
        service["module"],
        "--host", "0.0.0.0",
        "--port", str(port),
    ]

    # 热重载配置（仅在开发模式下启用）
    if os.getenv("NO_RELOAD", "").lower() != "true":
        cmd.append("--reload")
        # 添加模块目录作为监听目录
        if os.path.isdir(reload_dir):
            cmd.extend(["--reload-dir", reload_dir])

    print(f"  {service['name']:12} -> http://localhost:{port}")

    # 启动进程
    process = subprocess.Popen(
        cmd,
        cwd=BACKEND_DIR,
        stdout=None,
        stderr=None,
    )
    return process


def signal_handler(signum, frame):
    """信号处理函数"""
    stop_all()
    sys.exit(0)


def main():
    global stopping

    # 注册退出处理
    atexit.register(stop_all)

    # 信号处理 - 只处理 Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, signal_handler)

    print()
    print("=" * 60)
    print("  Education System - All Services Launcher")
    print("=" * 60)
    print()
    print("Starting services:")

    # 启动所有服务
    for service in SERVICES:
        proc = start_service(service)
        processes.append(proc)
        time.sleep(0.5)

    print()
    print("-" * 60)
    print("Hot-reload enabled - file changes auto-reload")
    print("Press Ctrl+C to stop all services")
    print("-" * 60)

    # 主循环 - 等待用户中断
    try:
        while not stopping:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        if not stopping:
            stop_all()


if __name__ == "__main__":
    main()
