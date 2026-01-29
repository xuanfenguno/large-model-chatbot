# 项目运行规则

## 后端运行命令
- 使用较高端口以避免权限问题（如8080、10001等）
- 推荐命令：`python manage.py runserver 8080`
- 如果端口8000出现权限问题，请使用其他端口

## API配置
- QWEN_API_KEY 已在 .env 文件中配置
- 环境变量通过 python-dotenv 自动加载

## 前端运行命令
- 在 chat/frontend 目录下执行：`npm run dev`
- 前端默认运行在 http://localhost:5173

## 系统集成
- 前端会自动连接到后端API
- 所有功能模块现已正常工作