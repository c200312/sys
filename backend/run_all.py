#!/usr/bin/env python
"""
统一服务启动脚本

同时启动主服务、AI PPT 服务、AI 写作服务，支持热重载

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
        "cwd": BACKEND_DIR,
    },
    {
        "name": "AI PPT",
        "port": int(os.getenv("AIPPT_PORT", 8002)),
        "module": "aippt.main:app",
        "cwd": BACKEND_DIR,
    },
    {
        "name": "AI Writing",
        "port": int(os.getenv("AIWRITING_PORT", 8003)),
        "module": "aiwriting.main:app",
        "cwd": BACKEND_DIR,
    },
]

processes = []


def start_service(service):
    """启动单个服务"""
    cmd = [
        sys.executable, "-m", "uvicorn",
        service["module"],
        "--host", "0.0.0.0",
        "--port", str(service["port"]),
        "--reload",
    ]

    print(f"🚀 Starting {service['name']} on http://localhost:{service['port']}")

    process = subprocess.Popen(
        cmd,
        cwd=service["cwd"],
        # 在 Windows 上需要特殊处理
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    return process


def kill_process_tree(pid):
    """在 Windows 上杀死进程树（包括所有子进程）"""
    if sys.platform == "win32":
        # 使用 taskkill 命令强制杀死进程树
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True,
            check=False
        )
    else:
        os.killpg(os.getpgid(pid), signal.SIGTERM)


def stop_all():
    """停止所有服务"""
    print("\n🛑 Stopping all services...")
    for proc in processes:
        if proc.poll() is None:  # 进程仍在运行
            try:
                kill_process_tree(proc.pid)
            except Exception as e:
                print(f"Warning: Failed to kill process {proc.pid}: {e}")

    # 等待进程结束
    for proc in processes:
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
            except Exception:
                pass

    print("✅ All services stopped")


def signal_handler(signum, frame):
    """处理终止信号"""
    stop_all()
    sys.exit(0)


def main():
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if sys.platform != "win32":
        signal.signal(signal.SIGQUIT, signal_handler)

    # 注册退出时的清理函数
    atexit.register(stop_all)

    print("=" * 60)
    print("📦 Education System - All Services Launcher")
    print("=" * 60)
    print()

    # 启动所有服务
    for service in SERVICES:
        proc = start_service(service)
        processes.append(proc)
        time.sleep(0.5)  # 稍微延迟，避免端口冲突

    print()
    print("=" * 60)
    print("✅ All services started with hot-reload enabled")
    print()
    print("Services:")
    for service in SERVICES:
        print(f"   • {service['name']}: http://localhost:{service['port']}")
    print()
    print("Press Ctrl+C to stop all services")
    print("=" * 60)

    # 监控进程状态
    try:
        while True:
            # 检查是否有进程意外退出
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    service = SERVICES[i]
                    print(f"⚠️  {service['name']} exited with code {proc.returncode}")
                    # 尝试重启
                    print(f"🔄 Restarting {service['name']}...")
                    processes[i] = start_service(service)

            time.sleep(2)
    except KeyboardInterrupt:
        stop_all()


if __name__ == "__main__":
    main()
