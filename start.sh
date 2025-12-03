#!/bin/bash

# 图像处理工作流平台启动脚本

set -e

MODE=${1:-dev}

echo "启动模式: $MODE"

# 检查依赖
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到 uv，请先安装: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 安装后端依赖
echo "安装后端依赖..."
cd "$(dirname "$0")"
uv sync

# 启动后端
echo "启动后端服务..."
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 5050 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
if [ "$MODE" = "dev" ]; then
    echo "启动前端开发服务器..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "安装前端依赖..."
        npm install
    fi
    
    npm run dev &
    FRONTEND_PID=$!
    
    echo "前端: http://localhost:5173"
    echo "后端API: http://localhost:5050"
    echo "API文档: http://localhost:5050/docs"
    echo ""
    echo "按 Ctrl+C 停止服务"
    
    # 等待用户中断
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    wait
else
    echo "生产模式需要构建前端并配置生产服务器"
    echo "后端运行在: http://localhost:5050"
    wait $BACKEND_PID
fi

