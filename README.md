# AI智能聊天机器人

基于大模型的聊天机器人系统，支持文本对话和图文混合输入。

## 技术栈

### 后端
- Python 3.9+
- Django 4.x
- Django REST Framework
- SQLite/MySQL
- CSDN AI API, OpenAI API, Anthropic API, Alibaba Cloud Qwen API

### 前端
- Vue 3
- Vite
- Element Plus
- Pinia

## 项目结构

```
.
├── backend/              # Django后端
│   ├── chatbot/         # 主应用
│   ├── config/          # 配置文件
│   ├── manage.py        # Django管理脚本
│   └── requirements.txt  # 依赖包
├── frontend/            # Vue前端
│   ├── src/             # 源代码
│   ├── public/          # 静态资源
│   ├── index.html       # 入口HTML
│   └── package.json     # 项目配置
├── .env                 # 环境变量配置
├── .inscode             # 项目运行配置
├── start_server.sh      # 一键启动脚本
├── restart_app.sh       # 重启脚本
└── README.md           # 项目说明
```

## 快速开始

### 1. 环境准备

#### 安装依赖
```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

#### 环境变量配置
1. 复制 `.env.example` 创建 `.env` 文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置数据库和大模型API密钥：
```env
# 数据库配置
DB_NAME=chatbot_db
DB_USER=root
DB_PASSWORD=root123
DB_HOST=localhost
DB_PORT=3306

# Django配置
DJANGO_SECRET_KEY=django-insecure-key-change-in-production
DEBUG=True

# 大模型API密钥配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 数据库初始化
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # 创建管理员账户
```

### 2. 启动服务

#### 一键启动（推荐）
```bash
# 确保脚本有执行权限
chmod +x start_server.sh
./start_server.sh
```

#### 手动启动
**启动后端服务**
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

**启动前端服务**
```bash
cd frontend
npm run dev
```

### 3. 访问应用
- 前端地址：http://localhost:3000
- 后端API：http://localhost:8000/api/v1/
- API文档：http://localhost:8000/swagger/

## API接口

### 用户认证接口

#### 用户登录
**接口地址：** `/api/v1/login/`
**请求方法：** POST
**请求参数：**
```json
{
  "username": "用户名",
  "password": "密码"
}
```

#### 用户注册
**接口地址：** `/api/v1/register/`
**请求方法：** POST
**请求参数：**
```json
{
  "username": "用户名",
  "email": "邮箱",
  "password": "密码"
}
```

### 聊天接口

#### 发送消息
**接口地址：** `/api/v1/messages/chat/`
**请求方法：** POST
**请求参数：**
```json
{
  "conversation_id": 1,
  "message": "用户消息内容",
  "image_url": "图片URL（可选）",
  "model": "gpt-4o-mini"  // 可选模型
}
```

#### 获取可用模型
**接口地址：** `/api/v1/models/`
**请求方法：** GET
**响应格式：**
```json
[
  {
    "id": "gpt-4o-mini",
    "name": "GPT-4o Mini",
    "provider": "OpenAI"
  },
  {
    "id": "claude-3-haiku",
    "name": "Claude 3 Haiku",
    "provider": "Anthropic"
  }
]
```

## 功能特性

- ✅ 支持多轮对话
- ✅ 支持图文混合输入
- ✅ 多大模型支持（OpenAI GPT系列、Anthropic Claude系列、DeepSeek、通义千问等）
- ✅ 模型切换功能
- ✅ 聊天记录管理
- ✅ 响应式设计
- ✅ 用户身份认证
- ✅ 实时聊天界面

## 支持的大模型

本项目集成了多种主流大模型：

### OpenAI系列
- GPT-4o, GPT-4o Mini, GPT-4 Turbo
- GPT-3.5 Turbo

### Anthropic系列
- Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku

### DeepSeek
- DeepSeek V3, DeepSeek R1

### 阿里巴巴通义千问
- Qwen Max, Qwen Plus, Qwen Turbo, Qwen VL系列

## 开发说明

### 后端开发
- 使用Django REST Framework构建API
- 集成多种大模型API服务
- 支持异步请求处理
- 实现对话历史管理

### 前端开发
- 使用Vue 3 Composition API
- Element Plus组件库
- Pinia状态管理
- 响应式设计适配各种设备

## 生产部署

### 前端部署
```bash
cd frontend
npm run build
```

### 后端部署
```bash
cd backend
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 许可证

MIT