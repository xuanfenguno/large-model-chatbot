#!/bin/bash

echo "=== 启动基于大模型的聊天机器人应用 ==="

# 检查后端服务器是否正在运行
if pgrep -f "python manage.py runserver" > /dev/null; then
    echo "✅ 后端服务器正在运行"
else
    echo "🚀 启动后端服务器..."
    cd backend
    python manage.py runserver 0.0.0.0:8000 &
    BACKEND_PID=$!
    echo "后端服务器 PID: $BACKEND_PID"
    cd ..
    # 等待后端服务器启动
    sleep 3
fi

# 检查前端服务器是否正在运行
if pgrep -f "vite" > /dev/null; then
    echo "✅ 前端开发服务器正在运行"
else
    echo "🚀 启动前端开发服务器..."
    cd frontend
    npm run dev -- --host 0.0.0.0 --port 3000 --no-open &
    FRONTEND_PID=$!
    echo "前端服务器 PID: $FRONTEND_PID"
    cd ..
    # 等待前端服务器启动
    sleep 3
fi

echo ""
echo "=== 应用已成功启动 ==="
echo "🌐 前端地址: http://localhost:3000"
echo "🔗 后端API地址: http://localhost:8000"
echo ""
echo "=== 功能说明 ==="
echo "1. 访问前端地址可以使用聊天机器人功能"
echo "2. 需要先登录系统才能开始聊天"
echo "3. 支持与大模型进行自然语言对话"
echo "4. 提供多种大模型引擎选择"
echo ""
echo "=== 停止服务 ==="
echo "使用 Ctrl+C 停止当前脚本，或使用以下命令:"
echo "pkill -f 'python manage.py runserver'"
echo "pkill -f 'vite'"