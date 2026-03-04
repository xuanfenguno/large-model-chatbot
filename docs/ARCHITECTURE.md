# AI聊天机器人系统架构图

## 系统架构总览

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              客户端层 (Frontend)                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Web 浏览器   │  │  Web 浏览器   │  │  Web 浏览器   │  │  Web 浏览器   │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                  │                │
│         └──────────────────┴──────────────────┴──────────────────┘                │
│                            │                                                     │
│                    ┌───────▼───────┐                                             │
│                    │  Vue 3 SPA    │                                             │
│                    └───────┬───────┘                                             │
│                            │                                                     │
│         ┌──────────────────┴──────────────────┐                                  │
│         │  前端路由 (Vue Router)               │                                  │
│         │  - /chat (聊天界面)                 │                                  │
│         │  - /function-router (多功能助手)    │                                  │
│         │  - /voice-chat (语音助手)           │                                  │
│         │  - /video-chat (视频通话)           │                                  │
│         │  - /settings (设置)                 │                                  │
│         │  - /login, /register (认证)         │                                  │
│         └──────────────────┬──────────────────┘                                  │
│                            │                                                     │
│         ┌──────────────────┴──────────────────┐                                  │
│         │  状态管理 (Pinia)                   │                                  │
│         │  - auth.js (认证状态)               │                                  │
│         │  - chat.js (聊天状态)               │                                  │
│         │  - settings.js (设置状态)           │                                  │
│         └─────────────────────────────────────┘                                  │
└────────────────────────────────────────────┬────────────────────────────────────┘
                                             │ HTTPS/REST API
                                             │ WebSocket (实时通信)
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            服务层 (Backend)                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    Django REST Framework (DRF)                          │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                              │                                                   │
│         ┌────────────────────┴────────────────────┐                             │
│         │  URL 路由 (urls.py)                      │                             │
│         │  - /api/v1/*                             │                             │
│         │  - /admin/*                              │                             │
│         │  - /api/v1/token/* (JWT认证)             │                             │
│         └────────────────────┬────────────────────┘                             │
│                              │                                                   │
│         ┌────────────────────┴────────────────────┐                             │
│         │  认证与权限 (JWT + Session)              │                             │
│         │  - IsAuthenticated                       │                             │
│         │  - IsAdminUser                           │                             │
│         │  - 权限控制                              │                             │
│         └────────────────────┬────────────────────┘                             │
│                              │                                                   │
│         ┌────────────────────┴────────────────────┐                             │
│         │  视图层 (Views)                          │                             │
│         │  ┌──────────────┐  ┌──────────────┐     │                             │
│         │  │ ChatView     │  │ VoiceView    │     │                             │
│         │  │ FunctionRouter│ │ KnowledgeBase │    │                             │
│         │  │ UserAuth     │  │ CallManager  │     │                             │
│         │  └──────────────┘  └──────────────┘     │                             │
│         └────────────────────┬────────────────────┘                             │
│                              │                                                   │
│         ┌────────────────────┴────────────────────┐                             │
│         │  业务逻辑层                              │                             │
│         │  ┌──────────────┐  ┌──────────────┐     │                             │
│         │  │ EnhancedAPI  │  │ FunctionRouter│    │                             │
│         │  │ - OpenAI     │  │ - 聊天       │     │                             │
│         │  │ - Gemini     │  │ - 笑话       │     │                             │
│         │  │ - Qwen       │  │ - 故事       │     │                             │
│         │  │ - Kimi       │  │ - 成语接龙   │     │                             │
│         │  │ - DeepSeek   │  │ - 翻译       │     │                             │
│         │  │ - Doubao     │  │ - 编程       │     │                             │
│         │  └──────────────┘  └──────────────┘     │                             │
│         └────────────────────┬────────────────────┘                             │
└────────────────────────────────────────────┬────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┴────────────────────────────────────┐
│                           数据层 (Data Layer)                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         Django ORM Models                               │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                              │                                                   │
│         ┌────────────────────┴────────────────────┐                             │
│         │  数据库模型                              │                             │
│         │  ┌──────────────┐  ┌──────────────┐     │                             │
│         │  │ User         │  │ UserProfile  │     │                             │
│         │  │ - 用户信息   │  │ - API密钥    │     │                             │
│         │  │ - 认证信息   │  │ - 头像       │     │                             │
│         │  └──────────────┘  └──────────────┘     │                             │
│         │  ┌──────────────┐  ┌──────────────┐     │                             │
│         │  │ Conversation │  │ Message      │     │                             │
│         │  │ - 会话管理   │  │ - 消息记录   │     │                             │
│         │  │ - 聊天模式   │  │ - 图片URL    │     │                             │
│         │  └──────────────┘  └──────────────┘     │                             │
│         │  ┌──────────────┐  ┌──────────────┐     │                             │
│         │  │ VoiceCall    │  │ PasswordReset│    │                             │
│         │  │ - 通话记录   │  │ - 密码重置   │     │                             │
│         │  │ - 通话状态   │  │ - 重置令牌   │     │                             │
│         │  └──────────────┘  └──────────────┘     │                             │
│         └────────────────────┬────────────────────┘                             │
│                              │                                                   │
│         ┌────────────────────┴────────────────────┐                             │
│         │  数据库 (MySQL/SQLite)                  │                             │
│         │  ┌──────────────┐  ┌──────────────┐     │                             │
│         │  │ users        │  │ chatbot_     │     │                             │
│         │  │ profiles     │  │ conversations│    │                             │
│         │  │ messages     │  │ voice_calls  │     │                             │
│         │  │ tokens       │  │ ...          │     │                             │
│         │  └──────────────┘  └──────────────┘     │                             │
│         └─────────────────────────────────────────┘                             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┴────────────────────────────────────┐
│                        外部服务层 (External Services)                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  OpenAI      │  │  Google      │  │  Alibaba     │  │  Moonshot    │        │
│  │  GPT API     │  │  Gemini API  │  │  Qwen API    │  │  Kimi API    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                          │
│  │  DeepSeek    │  │  ByteDance   │  │  Knowledge   │                          │
│  │  API         │  │  Doubao API  │  │  Base        │                          │
│  └──────────────┘  └──────────────┘  └──────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┴────────────────────────────────────┐
│                        中间件与工具 (Middleware)                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  CORS        │  │  Rate Limit  │  │  Cache       │  │  Security    │        │
│  │  Middleware  │  │  Middleware  │  │  Middleware  │  │  Middleware  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐                                             │
│  │  Django      │  │  Defender    │                                             │
│  │  Channels    │  │  (IP封禁)   │                                             │
│  └──────────────┘  └──────────────┘                                             │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 详细架构说明

### 1. 客户端层 (Frontend)

#### 技术栈
- **框架**: Vue 3 + Composition API
- **路由**: Vue Router 4
- **状态管理**: Pinia + pinia-plugin-persistedstate
- **UI组件**: Element Plus
- **构建工具**: Vite 5

#### 主要组件
```
src/
├── views/
│   ├── Home.vue              # 首页
│   ├── Login.vue             # 登录页面
│   ├── Register.vue          # 注册页面
│   ├── Chat.vue              # 聊天界面
│   ├── FunctionRouter.vue    # AI多功能助手
│   ├── VoiceChat.vue         # 语音助手
│   ├── VideoChat.vue         # 视频通话
│   ├── Settings.vue          # 设置页面
│   └── ...
├── stores/
│   ├── auth.js               # 认证状态管理
│   ├── chat.js               # 聊天状态管理
│   └── settings.js           # 设置状态管理
├── router/
│   └── index.js              # 路由配置
└── utils/
    ├── request.js            # HTTP请求封装
    ├── ai-api.js             # AI API调用
    └── ...
```

### 2. 服务层 (Backend)

#### 技术栈
- **框架**: Django 4.2 + Django REST Framework
- **认证**: JWT (SimpleJWT) + Session
- **实时通信**: Django Channels (WebSocket)
- **API文档**: drf-yasg (Swagger)

#### URL 路由结构
```
/api/v1/
├── /health-check/                    # 健康检查
├── /login/                           # 用户登录
├── /register/                        # 用户注册
├── /token/                           # JWT Token管理
│   ├── /obtain/                      # 获取token
│   ├── /refresh/                     # 刷新token
│   └── /verify/                      # 验证token
├── /conversations/                   # 会话管理 (ViewSet)
│   ├── /{id}/messages/               # 获取会话消息
│   └── /{id}/                        # 会话详情
├── /stream-chat/                     # 流式聊天
├── /function-router/                 # 功能路由
├── /models/                          # 可用模型列表
├── /upload-avatar/                   # 上传头像
├── /user-info/                       # 用户信息
├── /password/reset/                  # 密码重置
├── /voice/*                          # 语音通话API
│   ├── /initiate/                    # 发起通话
│   ├── /answer/                      # 接听通话
│   ├── /reject/                      # 拒绝通话
│   ├── /end/                         # 结束通话
│   ├── /status/                      # 通话状态
│   ├── /signaling/                   # 信令
│   ├── /history/                     # 通话历史
│   └── /active/                      # 活动通话
└── /knowledge-base/*                 # 知识库API
    ├── /search/                      # 搜索
    ├── /add/                         # 添加
    ├── /delete/{doc_id}/             # 删除
    ├── /sync/                        # 同步
    └── /stats/                       # 统计
```

#### 视图层 (Views)
```
chatbot/views.py
├── ConversationViewSet               # 会话管理 (ViewSet)
├── MessageViewSet                    # 消息管理 (ViewSet)
├── UserLoginView                     # 用户登录
├── UserRegistrationView              # 用户注册
├── stream_chat                       # 流式聊天
├── function_router                   # 功能路由
├── available_models                  # 获取模型列表
├── upload_avatar                     # 上传头像
├── get_user_info                     # 获取用户信息
├── request_password_reset            # 请求密码重置
└── reset_password                    # 重置密码
```

#### 业务逻辑层
```
chatbot/
├── enhanced_api.py                   # 增强的API包装器
│   ├── EnhancedApiWrapper
│   │   ├── get_available_providers() # 获取可用API提供者
│   │   ├── has_any_api_key()         # 检查API密钥
│   │   ├── get_first_available_model() # 获取第一个可用模型
│   │   └── get_available_models()    # 获取所有可用模型
│
├── function_router.py                # 功能路由系统
│   ├── FunctionRouter
│   │   ├── route_function()          # 路由到相应功能
│   │   ├── analyze_intent()          # 分析用户意图
│   │   ├── chat_handler()            # 聊天功能
│   │   ├── joke_handler()            # 笑话功能
│   │   ├── story_handler()           # 故事功能
│   │   ├── chengyu_handler()         # 成语接龙
│   │   ├── translation_handler()     # 翻译功能
│   │   ├── programming_handler()     # 编程功能
│   │   └── ... (17种功能)
│
└── api_base.py                       # API调用基类
    ├── BaseAIApi                     # 基类
    ├── OpenAIApi                     # OpenAI API
    ├── GoogleGeminiApi               # Gemini API
    ├── QwenApi                       # 通义千问 API
    ├── MoonshotKimiApi               # Kimi API
    └── DeepSeekApi                   # DeepSeek API
```

### 3. 数据层 (Data Layer)

#### 数据库模型 (Models)
```
chatbot/models.py
├── User                              # Django内置用户模型
├── UserProfile                       # 用户配置文件
│   ├── phone                         # 手机号
│   ├── avatar                        # 头像
│   ├── openai_api_key                # OpenAI API密钥
│   ├── deepseek_api_key              # DeepSeek API密钥
│   ├── qwen_api_key                  # 通义千问 API密钥
│   ├── gemini_api_key                # Gemini API密钥
│   ├── kimi_api_key                  # Kimi API密钥
│   ├── doubao_api_key                # 豆包 API密钥
│   └── qwen_code_api_key             # 通义千问代码 API密钥
├── Conversation                      # 会话模型
│   ├── user                          # 用户 (FK)
│   ├── title                         # 会话标题
│   ├── model                         # 使用的模型
│   ├── mode                          # 聊天模式 (text/voice/video)
│   └── timestamps                    # 时间戳
├── Message                           # 消息模型
│   ├── conversation                  # 会话 (FK)
│   ├── role                          # 角色 (user/assistant)
│   ├── message_type                  # 消息类型 (text/voice/video)
│   ├── content                       # 内容
│   ├── image_url                     # 图片URL
│   ├── audio_file                    # 语音文件
│   ├── audio_duration                # 语音时长
│   └── timestamps                    # 时间戳
├── VoiceCallRecord                   # 语音通话记录
│   ├── call_id                       # 通话ID
│   ├── caller                        # 主叫用户 (FK)
│   ├── callee                        # 被叫用户 (FK)
│   ├── status                        # 通话状态
│   ├── duration                      # 通话时长
│   └── device_info                   # 设备信息 (JSON)
└── PasswordResetToken                # 密码重置令牌
    ├── user                          # 用户 (FK)
    ├── token                         # 重置令牌
    └── expires_at                    # 过期时间
```

#### 数据库配置
```
config/settings.py
├── DATABASES
│   ├── default (MySQL)               # 主数据库
│   └── fallback (SQLite)             # 备用数据库
├── LLM_CONFIG                        # 大模型配置
│   ├── OPENAI_API_KEY
│   ├── GEMINI_API_KEY
│   ├── QWEN_API_KEY
│   ├── KIMI_API_KEY
│   ├── DEEPSEEK_API_KEY
│   └── DOUBAO_API_KEY
└── MEDIA_URL / MEDIA_ROOT            # 媒体文件配置
```

### 4. 外部服务层 (External Services)

#### 支持的AI模型提供商
```
外部API服务
├── OpenAI API
│   ├── GPT-3.5-turbo
│   ├── GPT-4
│   └── GPT-4-turbo
├── Google Gemini API
│   ├── Gemini Pro
│   └── Gemini Ultra
├── Alibaba Qwen API
│   ├── Qwen Turbo
│   ├── Qwen Plus
│   └── Qwen Max
├── Moonshot Kimi API
│   ├── Kimi Large
│   └── Kimi Exact
├── DeepSeek API
│   └── DeepSeek Chat
└── ByteDance Doubao API
    ├── Doubao Pro
    ├── Doubao Lite
    └── Doubao Ultra
```

#### 知识库系统
```
utils/knowledge_base.py
├── KnowledgeBaseManager
│   ├── search()                      # 搜索知识库
│   ├── add_document()                # 添加文档
│   ├── delete_document()             # 删除文档
│   └── sync()                        # 同步知识库
└── real_time_source                  # 实时知识源
```

### 5. 中间件层 (Middleware)

#### 自定义中间件
```
middleware/
├── cache_middleware.py
│   ├── QueryCountMiddleware          # 查询计数中间件
│   ├── PerformanceMonitoringMiddleware # 性能监控中间件
│   └── APICacheMiddleware            # API缓存中间件
├── ErrorHandlingMiddleware.py
│   └── ErrorHandlingMiddleware       # 统一错误处理
└── rate_limit.py
    └── rate_limit                    # 速率限制装饰器
```

#### Django中间件配置
```
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',          # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',                   # 内容安全策略
    'middleware.cache_middleware.QueryCountMiddleware',
    'middleware.cache_middleware.PerformanceMonitoringMiddleware',
    'middleware.cache_middleware.APICacheMiddleware',
    'chatbot.middleware.ErrorHandlingMiddleware',
    'config.middleware.performance.PerformanceMiddleware',
]
```

### 6. 认证与权限系统

#### JWT认证流程
```
┌──────────┐
│  用户    │
└────┬─────┘
     │ 1. 登录请求 (username + password)
     ▼
┌─────────────────┐
│  UserLoginView  │
└────┬────────────┘
     │ 2. 验证凭证
     ▼
┌─────────────────┐
│  Django Auth    │
└────┬────────────┘
     │ 3. 生成JWT Token
     ▼
┌─────────────────┐
│  返回响应       │
│  - access token │
│  - refresh token│
│  - user info    │
└────┬────────────┘
     │ 4. 存储到localStorage
     ▼
┌─────────────────┐
│  前端存储       │
│  - token        │
│  - user info    │
└────┬────────────┘
     │ 5. 每个请求携带Token
     ▼
┌─────────────────┐
│  后端验证       │
│  - 解码Token    │
│  - 验证有效期   │
│  - 获取用户     │
└────┬────────────┘
     │ 6. 授权访问
     ▼
┌─────────────────┐
│  返回数据       │
└─────────────────┘
```

#### 权限控制
```
权限级别
├── AllowAny                    # 公开接口
│   ├── /health-check/
│   ├── /login/
│   ├── /register/
│   └── /password/reset/request/
│
├── IsAuthenticated            # 认证用户
│   ├── /conversations/
│   ├── /stream-chat/
│   ├── /function-router/
│   ├── /upload-avatar/
│   └── /user-info/
│
└── IsAdminUser                # 管理员
    ├── /admin/*               # Django Admin
    └── 管理员专用接口
```

### 7. 部署架构

#### 开发环境
```
┌─────────────────────────────────────────────────────────────┐
│                    开发环境                                  │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Vite)    Backend (Django)    Database           │
│  http://localhost:5173  http://localhost:8000  MySQL       │
└─────────────────────────────────────────────────────────────┘
```

#### 生产环境
```
┌─────────────────────────────────────────────────────────────┐
│                    生产环境                                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   CDN        │  │  Nginx       │  │  Load        │      │
│  │  (静态文件)   │  │  反向代理    │  │  Balancer    │      │
│  └──────────────┘  └──────┬───────┘  └──────────────┘      │
│                           │                                  │
│                    ┌──────▼───────┐                          │
│                    │  Django App  │                          │
│                    │  + Channels  │                          │
│                    └──────┬───────┘                          │
│                           │                                  │
│                    ┌──────▼───────┐                          │
│                    │   MySQL      │                          │
│                    │   Cluster    │                          │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## 系统特点

### 1. 多模型支持
- 支持6个主流AI模型提供商
- 自动切换可用模型
- 用户可配置自己的API密钥

### 2. 实时通信
- WebSocket支持 (Django Channels)
- 流式响应 (SSE)
- 实时语音通话 (WebRTC)

### 3. 安全性
- JWT认证
- 速率限制
- IP封禁 (Defender)
- CORS配置
- CSP策略

### 4. 可扩展性
- 模块化设计
- API包装器模式
- 功能路由系统
- 知识库集成

### 5. 用户体验
- 响应式设计
- SPA路由
- 状态持久化
- 未读消息提醒

## 技术栈总结

### 前端
- Vue 3 + Composition API
- Element Plus
- Pinia
- Vue Router
- Vite

### 后端
- Django 4.2
- Django REST Framework
- Django Channels
- JWT
- MySQL/SQLite

### 运维
- Docker (可选)
- Nginx (生产环境)
- Gunicorn/Uvicorn (生产环境)
