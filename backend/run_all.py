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
import threading
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
stopping = False
stop_lock = threading.Lock()


def start_service(service):
    """启动单个服务（带热重载）"""
    # 确定需要监听的目录
    reload_dirs = []
    module_name = service["module"].split(":")[0].split(".")[0]
    reload_dir = os.path.join(service["cwd"], module_name)
    if os.path.isdir(reload_dir):
        reload_dirs = ["--reload-dir", reload_dir]

    cmd = [
        sys.executable, "-m", "uvicorn",
        service["module"],
        "--host", "0.0.0.0",
        "--port", str(service["port"]),
        "--reload",
        *reload_dirs,
    ]

    print(f"  Starting {service['name']} on http://localhost:{service['port']}")

    # 在 Windows 上，不使用 CREATE_NEW_PROCESS_GROUP 以避免信号传播问题
    process = subprocess.Popen(
        cmd,
        cwd=service["cwd"],
        stdout=None,  # 继承父进程的输出
        stderr=None,
    )
    return process


def kill_process_tree(pid):
    """杀死进程树"""
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
            pass


def stop_all():
    """停止所有服务"""
    global stopping

    with stop_lock:
        if stopping:
            return
        stopping = True

    print("\nStopping all services...")

    for proc in processes:
        if proc and proc.poll() is None:
            try:
                kill_process_tree(proc.pid)
            except Exception:
                pass

    # 等待进程结束
    for proc in processes:
        if proc:
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                except Exception:
                    pass

    print("All services stopped")


def main():
    global stopping

    print("=" * 60)
    print("Education System - All Services Launcher")
    print("=" * 60)
    print()

    # 启动所有服务
    for service in SERVICES:
        proc = start_service(service)
        processes.append(proc)
        time.sleep(0.5)

    print()
    print("=" * 60)
    print("All services started with hot-reload enabled")
    print()
    print("Services:")
    for service in SERVICES:
        print(f"   {service['name']}: http://localhost:{service['port']}")
    print()
    print("Hot-reload is active - changes will auto-reload")
    print("Press Ctrl+C to stop all services")
    print("=" * 60)

    # 主循环 - 只监控进程，不重启
    try:
        while not stopping:
            all_running = True
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    # 进程退出了，检查是否是热重载导致的
                    # uvicorn 热重载会重启子进程，但父进程不会退出
                    all_running = False

            if not all_running and not stopping:
                # 有进程退出，等待一下看是否是热重载
                time.sleep(1)
                # 检查是否所有进程都退出了
                all_exited = all(p.poll() is not None for p in processes)
                if all_exited:
                    print("All processes exited")
                    break

            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_all()


if __name__ == "__main__":
    main()
