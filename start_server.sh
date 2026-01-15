#!/bin/bash

# 启动基于大模型的聊天机器人应用

echo "=== 启动聊天机器人应用 ==="

# 检查是否已在项目根目录
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端服务器
echo "🔄 启动后端服务器..."
cd backend
if pgrep -f "python manage.py runserver" > /dev/null; then
    echo "✅ 后端服务器已在运行"
else
    echo "🚀 正在启动后端服务器..."
    nohup python manage.py runserver 0.0.0.0:8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ 后端服务器已启动 (PID: $BACKEND_PID)"
    # 等待服务器启动
    sleep 3
fi

# 检查后端服务器是否响应
echo "🔍 检查后端服务器响应..."
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/v1/health/" == "200"; then
    echo "✅ 后端服务器响应正常"
else
    echo "❌ 后端服务器未响应"
    # 检查服务器进程
    ps aux | grep python | grep -v grep
    cat ../backend.log
fi

# 启动前端服务器
cd ../frontend
echo "🔄 启动前端服务器..."
if pgrep -f "vite" > /dev/null; then
    echo "✅ 前端服务器已在运行"
else
    echo "🚀 正在启动前端服务器..."
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ 前端服务器已启动 (PID: $FRONTEND_PID)"
    # 等待服务器启动
    sleep 3
fi

# 返回项目根目录
cd ..

echo ""
echo "=== 应用启动完成 ==="
echo "📱 应用访问地址:"
echo "   - 前端应用: http://localhost:3000"
echo "   - 后端API: http://localhost:8000/api/v1/"
echo "   - API文档: http://localhost:8000/swagger/"
echo "   - ReDoc文档: http://localhost:8000/redoc/"
echo ""
echo "💡 功能特性:"
echo "   - 用户注册和登录"
echo "   - 多轮对话管理"
echo "   - 大模型聊天功能"
echo "   - 聊天历史记录"
echo "   - 多种模型引擎支持"
echo ""
echo "🔧 管理命令:"
echo "   - 查看后端日志: tail -f backend.log"
echo "   - 查看前端日志: tail -f frontend.log"
echo "   - 停止后端服务器: pkill -f 'python manage.py runserver'"
echo "   - 停止前端服务器: pkill -f 'vite'"
echo "   - 重启应用: ./restart_app.sh"