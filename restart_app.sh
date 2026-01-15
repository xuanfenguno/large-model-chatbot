#!/bin/bash
echo "=== 重启聊天机器人应用 ==="
echo "🔄 停止现有服务器..."
pkill -f 'python manage.py runserver' 2>/dev/null || true
pkill -f 'vite' 2>/dev/null || true
pkill -f 'npm run dev' 2>/dev/null || true
sleep 2
echo "✅ 服务器已停止"
echo "🔄 重新启动应用..."
./start_server.sh
