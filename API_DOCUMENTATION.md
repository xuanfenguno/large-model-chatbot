# AI聊天机器人API文档

## 概述

这是一个基于Django REST Framework的AI聊天机器人后端API，支持多种AI模型提供商（OpenAI、Google Gemini、Moonshot Kimi、阿里云通义千问等）。

## 认证

所有需要认证的API端点都需要在请求头中包含JWT Token：
```
Authorization: Bearer <your-jwt-token>
```

## API端点

### 通用端点

#### 健康检查
```
GET /api/v1/health/
```

**响应示例：**
```json
{
  "status": "ok",
  "message": "AI聊天机器人服务正常运行"
}
```

#### 用户登录
```
POST /api/v1/login/
```

**请求体：**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**响应示例：**
```json
{
  "refresh": "refresh_token",
  "access": "access_token",
  "username": "your_username",
  "email": "your_email"
}
```

#### 用户注册
```
POST /api/v1/register/
```

**请求体：**
```json
{
  "username": "new_username",
  "email": "new@email.com",
  "password": "new_password"
}
```

**响应示例：**
```json
{
  "refresh": "refresh_token",
  "access": "access_token",
  "username": "new_username",
  "email": "new@email.com"
}
```

### 会话管理

#### 获取会话列表
```
GET /api/v1/conversations/
```

**响应示例：**
```json
[
  {
    "id": 1,
    "user": 1,
    "title": "我的会话",
    "model": "gpt-3.5-turbo",
    "created_at": "2023-10-01T12:00:00Z",
    "updated_at": "2023-10-01T12:00:00Z"
  }
]
```

#### 创建会话
```
POST /api/v1/conversations/
```

**请求体：**
```json
{
  "title": "新会话",
  "model": "gpt-3.5-turbo"
}
```

#### 获取会话详情
```
GET /api/v1/conversations/{id}/
```

#### 更新会话
```
PUT /api/v1/conversations/{id}/
```

#### 删除会话
```
DELETE /api/v1/conversations/{id}/
```

#### 获取会话消息
```
GET /api/v1/conversations/{id}/messages/
```

### 消息管理

#### 获取消息列表
```
GET /api/v1/messages/
```

#### 发送消息
```
POST /api/v1/messages/chat/
```

**请求体：**
```json
{
  "conversation_id": 1,
  "message": "你好，世界！",
  "model": "gpt-3.5-turbo",
  "image_url": "optional_image_url"
}
```

**响应示例：**
```json
{
  "conversation_id": 1,
  "user_message": {
    "id": 1,
    "conversation": 1,
    "role": "user",
    "content": "你好，世界！",
    "created_at": "2023-10-01T12:00:00Z"
  },
  "ai_message": {
    "id": 2,
    "conversation": 1,
    "role": "assistant",
    "content": "你好！有什么我可以帮你的吗？",
    "created_at": "2023-10-01T12:00:05Z"
  },
  "status": "completed"
}
```

### 模型管理

#### 获取可用模型列表
```
GET /api/v1/models/
```

**响应示例：**
```json
[
  {
    "id": "gpt-3.5-turbo",
    "name": "GPT-3.5 Turbo",
    "provider": "OpenAI"
  },
  {
    "id": "gemini-pro", 
    "name": "Gemini Pro",
    "provider": "Google"
  }
]
```

### 微信OAuth登录

#### 获取微信授权URL
```
GET /api/v1/auth/wechat/url/
```

#### 微信授权回调
```
GET /api/v1/auth/wechat/callback/
```

## 错误处理

所有错误响应遵循以下格式：
```json
{
  "error": "错误信息描述"
}
```

常见的HTTP状态码：
- `200`: 成功
- `201`: 创建成功
- `400`: 请求错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源未找到
- `500`: 服务器内部错误

## 限流

为了保护服务器，某些API端点可能有限流限制。如果超过限制，将返回 `429 Too Many Requests` 状态码。

## 安全注意事项

1. 所有敏感API密钥应存储在环境变量中
2. JWT令牌有过期时间，请妥善处理刷新逻辑
3. 避免在客户端暴露API密钥
4. 在生产环境中启用HTTPS