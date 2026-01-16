@echo off
chcp 65001 >nul
echo === 启动基于大模型的聊天机器人应用 ===

echo 启动后端服务器...
start "Backend Server" cmd /k "cd /d %~dp0\backend && python manage.py runserver 8000"

echo 等待后端服务器启动...
timeout /t 8 /nobreak >nul

echo 启动前端服务器...
start "Frontend Server" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo === 应用启动完成 ===
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:8000
echo.
echo 按任意键关闭窗口...
pause >nul
