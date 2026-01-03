#!/bin/bash

# 教育系统启动脚本 (Windows Git Bash / WSL 兼容)
# 用法: bash start.sh [start|stop|restart|status]

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/.pids"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 检测是否为 Windows 环境
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OS" == "Windows_NT" ]]; then
    IS_WINDOWS=true
else
    IS_WINDOWS=false
fi

# 服务配置
SERVICES=(
    "8080:app.main:app:Main_API"
    "8002:aippt.main:app:AI_PPT"
    "8003:aiwriting.main:app:AI_Writing"
    "8004:airag.main:app:AI_RAG"
)
FRONTEND_PORT=3000

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo ""
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# 停止端口占用的进程
kill_port() {
    local port=$1
    if [ "$IS_WINDOWS" = true ]; then
        # Windows: 使用 netstat + taskkill
        for pid in $(netstat -ano 2>/dev/null | grep ":$port" | grep "LISTENING" | awk '{print $5}' | sort -u); do
            if [ -n "$pid" ] && [ "$pid" != "0" ]; then
                taskkill //F //PID "$pid" >/dev/null 2>&1
            fi
        done
    else
        # Linux/Mac
        lsof -ti:$port | xargs kill -9 2>/dev/null
    fi
}

# 检查端口是否在运行
check_port() {
    local port=$1
    if [ "$IS_WINDOWS" = true ]; then
        netstat -ano 2>/dev/null | grep ":$port" | grep "LISTENING" >/dev/null 2>&1
    else
        lsof -i:$port >/dev/null 2>&1
    fi
}

# 停止服务
do_stop() {
    print_header "Education System - Stopping All Services"

    # 停止前端
    echo -e "[*] 停止前端服务..."
    kill_port $FRONTEND_PORT

    # 停止后端
    echo -e "[*] 停止后端服务..."
    for service in "${SERVICES[@]}"; do
        port=$(echo "$service" | cut -d: -f1)
        kill_port $port
    done

    # 清理 PID 文件
    rm -f "$PID_FILE"

    echo -e "[*] 所有服务已停止"
    echo ""
}

# 启动服务
do_start() {
    print_header "Education System - Starting All Services"

    # 检查是否已运行
    if [ -f "$PID_FILE" ]; then
        echo -e "${YELLOW}[!] 服务可能已在运行，先执行停止...${NC}"
        do_stop
        sleep 2
    fi

    cd "$BACKEND_DIR"

    # 设置 Python 路径（Windows vs Linux）
    if [ "$IS_WINDOWS" = true ]; then
        PYTHON_CMD="$BACKEND_DIR/.venv/Scripts/python.exe"
        NPM_CMD="npm.cmd"
        PNPM_CMD="pnpm.cmd"
    else
        PYTHON_CMD="$BACKEND_DIR/.venv/bin/python"
        NPM_CMD="npm"
        PNPM_CMD="pnpm"
    fi

    # 加载环境变量
    if [ -f "$BACKEND_DIR/.env" ]; then
        set -a
        source "$BACKEND_DIR/.env"
        set +a
    fi

    # 启动后端服务
    echo -e "[*] 启动后端服务..."
    for service in "${SERVICES[@]}"; do
        port=$(echo "$service" | cut -d: -f1)
        module=$(echo "$service" | cut -d: -f2-3)
        name=$(echo "$service" | cut -d: -f4)

        # 确保端口空闲
        kill_port $port
        sleep 0.3

        # 启动 uvicorn
        "$PYTHON_CMD" -m uvicorn "$module" --host 0.0.0.0 --port $port > "$LOG_DIR/${name}.log" 2>&1 &
        echo $! >> "$PID_FILE"
        echo -e "    ${GREEN}$name${NC} -> http://localhost:$port"
        sleep 0.5
    done

    # 启动前端
    echo -e "[*] 启动前端服务..."
    cd "$FRONTEND_DIR"
    $PNPM_CMD -v || $NPM_CMD install -g pnpm
    [ ! -d "node_modules" ] && $PNPM_CMD install
    $PNPM_CMD run dev > "$LOG_DIR/frontend.log" 2>&1 &
    echo $! >> "$PID_FILE"
    echo -e "    ${GREEN}Frontend${NC} -> http://localhost:$FRONTEND_PORT"

    echo ""
    echo "------------------------------------------------------------"
    echo "  日志目录: logs/"
    echo "  停止: bash start.sh stop"
    echo "  重启: bash start.sh restart"
    echo "  状态: bash start.sh status"
    echo "------------------------------------------------------------"
    echo ""
}

# 检查状态
do_status() {
    print_header "Education System - Service Status"

    # 检查后端端口
    for service in "${SERVICES[@]}"; do
        port=$(echo "$service" | cut -d: -f1)
        name=$(echo "$service" | cut -d: -f4)
        if check_port $port; then
            echo -e "${GREEN}[OK]${NC} $name (端口 $port) 运行中"
        else
            echo -e "${RED}[--]${NC} $name (端口 $port) 未运行"
        fi
    done

    # 检查前端端口
    if check_port $FRONTEND_PORT; then
        echo -e "${GREEN}[OK]${NC} Frontend (端口 $FRONTEND_PORT) 运行中"
    else
        echo -e "${RED}[--]${NC} Frontend (端口 $FRONTEND_PORT) 未运行"
    fi

    echo ""
}

# 主逻辑
case "${1:-start}" in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    restart)
        print_header "Education System - Restarting All Services"
        do_stop
        sleep 2
        do_start
        ;;
    status)
        do_status
        ;;
    *)
        echo "用法: bash start.sh [start|stop|restart|status]"
        exit 1
        ;;
esac
