# 基于大模型的聊天机器人应用

这是一个基于大语言模型的智能聊天机器人应用，支持多种AI模型、语音通话、知识库等功能。

## 功能特性

- 🤖 支持多种大语言模型（GPT、Qwen、Gemini等）
- 💬 实时聊天对话功能
- 🔐 用户认证系统（注册/登录）
- 👤 个人资料管理
- 📚 知识库集成
- 📞 语音通话功能
- ⚡ 流式响应
- 📱 响应式界面

## 技术栈

### 后端
- Django 4.2+
- Django REST Framework
- JWT 认证
- Channels (WebSocket支持)

### 前端
- Vue 3
- Element Plus UI组件库
- Pinia 状态管理
- Axios HTTP客户端
- Vite 构建工具

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Redis (可选，用于缓存和会话)

### 后端启动

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置数据库
```bash
python manage.py migrate
```

4. 创建超级用户（可选）
```bash
python manage.py createsuperuser
```

5. 启动后端服务器
```bash
python manage.py runserver 8080
```

### 前端启动

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动前端开发服务器
```bash
npm run dev
```

4. 访问应用
打开浏览器访问 `http://127.0.0.1:5173`

## 登录凭据

默认管理员账户：
- 用户名：`admin`
- 密码：`admin123`

## API端点

- 健康检查：`GET /api/v1/health-check/`
- 用户登录：`POST /api/v1/login/`
- 用户注册：`POST /api/v1/register/`
- 会话管理：`GET/POST /api/v1/conversations/`
- 流式聊天：`POST /api/v1/stream-chat/`

## 环境配置

复制 `.env.example` 文件并重命名为 `.env`，然后填入相应的配置项：

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DB_HOST=localhost
DB_PORT=3306
DB_NAME=chatbot_db
DB_USER=root
DB_PASSWORD=root123
OPENAI_API_KEY=your-openai-api-key
QWEN_API_KEY=your-qwen-api-key
GEMINI_API_KEY=your-gemini-api-key
```

## 项目结构

```
chat/
├── backend/          # Django后端
│   ├── chatbot/      # 主应用
│   ├── config/       # 配置文件
│   └── manage.py
├── frontend/         # Vue前端
│   ├── src/
│   ├── public/
│   └── package.json
└── docs/             # 文档
```

## 部署

### 生产环境部署

1. 修改 `backend/config/settings.py` 中的生产环境配置
2. 设置适当的 `ALLOWED_HOSTS`
3. 配置Web服务器（如Nginx）
4. 使用WSGI服务器（如Gunicorn）部署Django应用

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 许可证

本项目采用 MIT 许可证。