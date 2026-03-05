# 数据库表清单

## 一、数据库表概览

本项目共包含 **7个核心数据库表**，其中：

- **Django内置表** (2个): `auth_user`, `django_session`
- **项目自定义表** (5个): `chatbot_conversation`, `chatbot_message`, `chatbot_userprofile`, `chatbot_passwordresettoken`, `chatbot_voicecallrecord`

---

## 二、详细表清单

### 1. auth_user (用户表) - Django内置

**说明**: Django认证系统内置的用户表，存储用户基本信息

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 用户ID | 主键 |
| username | String | 用户名 | 唯一，必填 |
| password | String | 密码 | 加密存储 |
| email | String | 邮箱 | 可为空 |
| first_name | String | 名 | 可为空 |
| last_name | String | 姓 | 可为空 |
| is_active | Boolean | 是否激活 | 默认 true |
| is_staff | Boolean | 是否为员工 | 默认 false |
| is_superuser | Boolean | 是否为超级用户 | 默认 false |
| date_joined | DateTime | 注册时间 | 自动设置 |
| last_login | DateTime | 最后登录时间 | 可为空 |

**关系**:
- 一对多 → chatbot_userprofile (一对一扩展)
- 一对多 → chatbot_conversation (用户创建的会话)
- 一对多 → chatbot_message (用户发送的消息)
- 一对多 → chatbot_passwordresettoken (密码重置令牌)
- 一对多 → chatbot_voicecallrecord (作为主叫或被叫)

---

### 2. chatbot_userprofile (用户配置表)

**说明**: 扩展用户配置信息，存储用户个性化设置和API密钥

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 配置ID | 主键 |
| user_id | Integer | 用户ID | 外键 → auth_user.id (一对一) |
| phone | String | 手机号 | 可为空 |
| avatar | Image | 头像 | 可为空 |
| openai_api_key | Text | OpenAI API密钥 | 可为空 |
| deepseek_api_key | Text | DeepSeek API密钥 | 可为空 |
| qwen_api_key | Text | 通义千问API密钥 | 可为空 |
| gemini_api_key | Text | Gemini API密钥 | 可为空 |
| kimi_api_key | Text | Kimi API密钥 | 可为空 |
| doubao_api_key | Text | 豆包API密钥 | 可为空 |
| qwen_code_api_key | Text | 通义千问代码API密钥 | 可为空 |
| created_at | DateTime | 创建时间 | 自动设置 |
| updated_at | DateTime | 更新时间 | 自动更新 |

**关系**:
- 一对一 ← auth_user (用户配置属于一个用户)

**说明**:
- 扩展Django内置User模型
- 存储用户的API密钥配置
- 存储用户个性化设置

---

### 3. chatbot_conversation (会话表)

**说明**: 存储用户与AI助手的会话信息，实现多轮对话的上下文管理

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 会话ID | 主键 |
| user_id | Integer | 用户ID | 外键 → auth_user.id |
| title | String | 会话标题 | 必填 |
| created_at | DateTime | 创建时间 | 自动设置 |
| updated_at | DateTime | 更新时间 | 自动更新 |
| model | String | 使用的模型 | 默认 'gpt-3.5-turbo' |
| mode | String | 聊天模式 | 默认 'text' |

**聊天模式 (mode)**:
- `text` - 文字聊天
- `voice` - 语音通话
- `video` - 视频通话

**关系**:
- 多对一 → auth_user (多个会话属于一个用户)
- 一对多 → chatbot_message (一个会话包含多条消息)

**说明**:
- 实现多轮对话的上下文管理
- 通过 `user_id` 关联用户
- 通过 `model` 字段记录使用的AI模型
- 通过 `mode` 字段记录聊天模式

---

### 4. chatbot_message (消息表/聊天记录表)

**说明**: 记录用户与AI助手的对话内容，即"聊天记录"

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 消息ID | 主键 |
| conversation_id | Integer | 会话ID | 外键 → chatbot_conversation.id |
| role | String | 角色 | 'user' 或 'assistant' |
| message_type | String | 消息类型 | 默认 'text' |
| content | Text | 消息内容 | 必填 |
| created_at | DateTime | 创建时间 | 自动设置 |
| image_url | URL | 图片URL | 可为空 |
| is_read | Boolean | 是否已读 | 默认 false |
| audio_file | File | 语音文件 | 可为空 |
| audio_duration | Float | 语音时长(秒) | 可为空 |
| transcription_confidence | Float | 语音识别置信度 | 可为空 |

**角色 (role)**:
- `user` - 用户发送的消息
- `assistant` - 助手回复的消息

**消息类型 (message_type)**:
- `text` - 文本消息
- `voice` - 语音消息
- `video` - 视频消息

**关系**:
- 多对一 → chatbot_conversation (多条消息属于一个会话)

**说明**:
- 记录用户与AI助手的对话内容
- 支持文本、语音、视频多种消息类型
- 通过 `conversation_id` 实现多轮对话上下文管理
- **这就是你提到的"聊天记录"实体**

---

### 5. chatbot_passwordresettoken (密码重置令牌表)

**说明**: 存储用户密码重置请求的令牌

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 令牌ID | 主键 |
| user_id | Integer | 用户ID | 外键 → auth_user.id |
| token | String | 重置令牌 | 唯一 |
| created_at | DateTime | 创建时间 | 自动设置 |
| expires_at | DateTime | 过期时间 | 必填 |

**关系**:
- 多对一 → auth_user (多个重置令牌属于一个用户)

**说明**:
- 用户忘记密码时生成重置令牌
- 通过邮箱发送重置链接
- 令牌有过期时间

---

### 6. chatbot_voicecallrecord (语音通话记录表)

**说明**: 记录用户之间的语音通话信息

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 通话记录ID | 主键 |
| call_id | String | 通话ID | 唯一 |
| caller_id | Integer | 主叫用户ID | 外键 → auth_user.id |
| callee_id | Integer | 被叫用户ID | 外键 → auth_user.id |
| status | String | 通话状态 | 默认 'pending' |
| initiated_at | DateTime | 发起时间 | 自动设置 |
| accepted_at | DateTime | 接听时间 | 可为空 |
| ended_at | DateTime | 结束时间 | 可为空 |
| duration | Integer | 通话时长(秒) | 默认 0 |
| caller_device_info | JSON | 主叫设备信息 | 可为空 |
| callee_device_info | JSON | 被叫设备信息 | 可为空 |

**通话状态 (status)**:
- `pending` - 等待接听
- `accepted` - 已接听
- `rejected` - 已拒绝
- `ended` - 已结束
- `missed` - 未接听

**关系**:
- 多对一 → auth_user (主叫用户)
- 多对一 → auth_user (被叫用户)

**说明**:
- 记录语音通话的完整信息
- 支持通话状态追踪
- 存储通话时长和设备信息

---

### 7. django_session (会话表) - Django内置

**说明**: Django会话框架使用的表，存储用户会话信息

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| session_key | String | 会话密钥 | 主键 |
| session_data | Text | 会话数据 | 加密存储 |
| expire_date | DateTime | 过期时间 | 必填 |

**关系**:
- 无外键关联

**说明**:
- 存储用户的登录状态
- 自动过期机制
- 支持分布式会话

---

## 三、核心实体关系图 (E-R图)

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                           核心实体 E-R 图 (Entity-Relationship Diagram)                    │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                  auth_user (用户)                                  │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - username (UNIQUE)                                                         │  │  │
│  │  │  - password (HASH)                                                           │  │  │
│  │  │  - email                                                                     │  │  │
│  │  │  - first_name                                                                │  │  │
│  │  │  - last_name                                                                 │  │  │
│  │  │  - is_active                                                                 │  │  │
│  │  │  - is_staff                                                                  │  │  │
│  │  │  - is_superuser                                                              │  │  │
│  │  │  - date_joined                                                               │  │  │
│  │  │  - last_login                                                                │  │  │
│  │  └──────────────────────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│                                    ▲    ▲    ▲                                             │
│                                    │ 1  │ 1  │ 1                                           │
│                                    │    │    │                                             │
│                                    │    │    └──────────────────┐                         │
│                                    │    │                       │                         │
│                                    │    │                       ▼                         │
│  ┌─────────────────────────────────┴────┴───────────────────────────────────────────────┐  │
│  │                             chatbot_userprofile (用户配置)                          │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - user_id (FK → auth_user.id) [一对一]                                      │  │  │
│  │  │  - phone                                                                     │  │  │
│  │  │  - avatar                                                                    │  │  │
│  │  │  - openai_api_key                                                            │  │  │
│  │  │  - deepseek_api_key                                                          │  │  │
│  │  │  - qwen_api_key                                                              │  │  │
│  │  │  - gemini_api_key                                                            │  │  │
│  │  │  - kimi_api_key                                                              │  │  │
│  │  │  - doubao_api_key                                                            │  │  │
│  │  │  - qwen_code_api_key                                                         │  │  │
│  │  │  - created_at                                                                │  │  │
│  │  │  - updated_at                                                                │  │  │
│  │  └──────────────────────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│                                    ▲                                                       │
│                                    │ 1:N (一对多)                                          │
│                                    │                                                       │
│                                    │                                                       │
│  ┌─────────────────────────────────┴────────────────────────────────────────────────────┐  │
│  │                              chatbot_conversation (会话)                            │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - user_id (FK → auth_user.id) [多对一]                                      │  │  │
│  │  │  - title                                                                     │  │  │
│  │  │  - created_at                                                                │  │  │
│  │  │  - updated_at                                                                │  │  │
│  │  │  - model                                                                     │  │  │
│  │  │  - mode (text/voice/video)                                                  │  │  │
│  │  └──────────────────────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│                                    ▲                                                       │
│                                    │ 1:N (一对多)                                          │
│                                    │                                                       │
│                                    │                                                       │
│  ┌─────────────────────────────────┴────────────────────────────────────────────────────┐  │
│  │                             chatbot_message (聊天记录)                              │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - conversation_id (FK → chatbot_conversation.id) [多对一]                  │  │  │
│  │  │  - role (user/assistant)                                                    │  │  │
│  │  │  - message_type (text/voice/video)                                          │  │  │
│  │  │  - content                                                                   │  │  │
│  │  │  - created_at                                                                │  │  │
│  │  │  - image_url                                                                 │  │  │
│  │  │  - is_read                                                                   │  │  │
│  │  │  - audio_file                                                                │  │  │
│  │  │  - audio_duration                                                            │  │  │
│  │  │  - transcription_confidence                                                  │  │  │
│  │  └──────────────────────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│                                    ▲                                                       │
│                                    │ 1:N (一对多)                                          │
│                                    │                                                       │
│                                    │                                                       │
│  ┌─────────────────────────────────┴────────────────────────────────────────────────────┐  │
│  │                         chatbot_passwordresettoken (密码重置令牌)                   │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - user_id (FK → auth_user.id) [多对一]                                      │  │  │
│  │  │  - token (UNIQUE)                                                            │  │  │
│  │  │  - created_at                                                                │  │  │
│  │  │  - expires_at                                                                │  │  │
│  │  └──────────────────────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│                                    ▲                                                       │
│                                    │ 1:N (一对多)                                          │
│                                    │                                                       │
│                                    │                                                       │
│  ┌─────────────────────────────────┴────────────────────────────────────────────────────┐  │
│  │                        chatbot_voicecallrecord (语音通话记录)                       │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - call_id (UNIQUE)                                                          │  │  │
│  │  │  - caller_id (FK → auth_user.id) [主叫]                                      │  │  │
│  │  │  - callee_id (FK → auth_user.id) [被叫]                                      │  │  │
│  │  │  - status                                                                    │  │  │
│  │  │  - initiated_at                                                              │  │  │
│  │  │  - accepted_at                                                               │  │  │
│  │  │  - ended_at                                                                  │  │  │
│  │  │  - duration                                                                  │  │  │
│  │  │  - caller_device_info                                                        │  │  │
│  │  │  - callee_device_info                                                        │  │  │
│  │  └──────────────────────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 四、核心实体关系说明

### 1. 用户 (auth_user) ↔ 聊天记录 (chatbot_message) - 一对多

```
用户 (1) ──< 聊天记录 (N)
```

- **一个用户可以有多条聊天记录**
- **一条聊天记录只属于一个用户**
- **实现方式**: 通过 `chatbot_message.user_id` 外键关联

### 2. 用户 (auth_user) ↔ 会话 (chatbot_conversation) - 一对多

```
用户 (1) ──< 会话 (N)
```

- **一个用户可以创建多个会话**
- **一个会话只属于一个用户**
- **实现方式**: 通过 `chatbot_conversation.user_id` 外键关联

### 3. 会话 (chatbot_conversation) ↔ 聊天记录 (chatbot_message) - 一对多

```
会话 (1) ──< 聊天记录 (N)
```

- **一个会话可以包含多条消息**
- **一条消息只属于一个会话**
- **实现方式**: 通过 `chatbot_message.conversation_id` 外键关联
- **作用**: 实现多轮对话的上下文管理

### 4. 用户 (auth_user) ↔ 用户配置 (chatbot_userprofile) - 一对一

```
用户 (1) ── 用户配置 (1)
```

- **一个用户只有一个用户配置**
- **一个用户配置只属于一个用户**
- **实现方式**: 通过 `chatbot_userprofile.user_id` 外键关联 (OneToOneField)

### 5. 用户 (auth_user) ↔ 密码重置令牌 (chatbot_passwordresettoken) - 一对多

```
用户 (1) ──< 密码重置令牌 (N)
```

- **一个用户可以有多个密码重置令牌**
- **一个令牌只属于一个用户**
- **实现方式**: 通过 `chatbot_passwordresettoken.user_id` 外键关联

### 6. 用户 (auth_user) ↔ 语音通话记录 (chatbot_voicecallrecord) - 一对多

```
用户 (1) ──< 语音通话记录 (N) [作为主叫]
用户 (1) ──< 语音通话记录 (N) [作为被叫]
```

- **一个用户可以发起或接收多通电话**
- **一次通话涉及两个用户（主叫和被叫）**
- **实现方式**: 通过 `chatbot_voicecallrecord.caller_id` 和 `callee_id` 两个外键关联

---

## 五、数据库表统计

| 类别 | 表数量 | 说明 |
|-----|-------|------|
| Django内置表 | 2 | auth_user, django_session |
| 项目自定义表 | 5 | chatbot_conversation, chatbot_message, chatbot_userprofile, chatbot_passwordresettoken, chatbot_voicecallrecord |
| **总计** | **7** | |

---

## 六、核心实体总结

### 核心业务实体 (5个)

1. **auth_user** - 用户实体
2. **chatbot_userprofile** - 用户配置实体
3. **chatbot_conversation** - 会话实体
4. **chatbot_message** - 聊天记录实体
5. **chatbot_voicecallrecord** - 语音通话记录实体

### 辅助实体 (1个)

6. **chatbot_passwordresettoken** - 密码重置令牌实体

### 系统实体 (1个)

7. **django_session** - 会话存储实体

---

## 七、E-R图在论文中的应用

### 图 4-3 核心实体 E-R 图

在论文中，可以使用以下格式的E-R图：

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                         图 4-3 核心实体 E-R 图 (Entity-Relationship Diagram)              │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  ┌───────────────┐      1:N       ┌───────────────┐      1:N       ┌───────────────┐       │
│  │   auth_user   │───────────────▶│chatbot_conv.  │───────────────▶│chatbot_msg.   │       │
│  ├───────────────┤                ├───────────────┤                ├───────────────┤       │
│  │ PK id         │                │ PK id         │                │ PK id         │       │
│  │ username      │                │ user_id (FK)  │                │ conv_id (FK)  │       │
│  │ password      │                │ title         │                │ role          │       │
│  │ email         │                │ created_at    │                │ content       │       │
│  │ ...           │                │ model         │                │ created_at    │       │
│  └───────────────┘                │ mode          │                │ ...           │       │
│                                   └───────────────┘                └───────────────┘       │
│                                          ▲                                                   │
│                                          │ 1:1                                               │
│                                          │                                                   │
│                                   ┌──────┴──────┐                                           │
│                                   │chatbot_profile│                                         │
│                                   ├─────────────┤                                           │
│                                   │ user_id (FK)│                                           │
│                                   │ phone       │                                           │
│                                   │ avatar      │                                           │
│                                   │ api_keys... │                                           │
│                                   └─────────────┘                                           │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 说明

1. **auth_user (用户)**: 系统的核心实体，代表系统用户
2. **chatbot_profile (用户配置)**: 扩展用户信息，存储API密钥等配置
3. **chatbot_conversation (会话)**: 实现多轮对话的上下文管理
4. **chatbot_msg (消息/聊天记录)**: 记录用户与AI助手的对话内容

### 关系说明

- **auth_user ↔ chatbot_profile**: 一对一关系，每个用户有且仅有一个配置文件
- **auth_user ↔ chatbot_conversation**: 一对多关系，一个用户可以创建多个会话
- **chatbot_conversation ↔ chatbot_msg**: 一对多关系，一个会话包含多条消息

---

## 八、总结

本项目的数据库设计遵循以下原则：

✅ **高内聚**: 每个表专注于特定功能  
✅ **低耦合**: 表之间通过外键关联，减少直接依赖  
✅ **可扩展**: 易于添加新的表和字段  
✅ **规范化**: 符合数据库设计范式  

这种设计方式使得系统更加灵活、可维护，并且便于扩展新的功能。
