# 核心实体 E-R 图

## 一、核心实体关系说明

本平台的核心实体包括 **用户（User）** 和 **聊天记录（ChatRecord）**，二者为一对多的关联关系（一个用户对应多条聊天记录，一条聊天记录仅属于一个用户）；同时，聊天记录实体包含 **会话（Session）** 的相关属性，通过会话 ID 实现多轮对话的上下文管理。

---

## 二、E-R 图

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                           核心实体 E-R 图 (Entity-Relationship Diagram)                    │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                    用户 (User)                                      │  │
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
│                                    ▲                                                       │
│                                    │ 1:N (一对多)                                          │
│                                    │                                                       │
│                                    │                                                       │
│  ┌─────────────────────────────────┴────────────────────────────────────────────────────┐  │
│  │                              用户配置 (UserProfile)                                  │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - user_id (FK → User.id) [一对一]                                           │  │  │
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
│  │                                会话 (Conversation)                                 │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - user_id (FK → User.id) [多对一]                                           │  │  │
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
│  │                               聊天记录 (Message)                                   │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - conversation_id (FK → Conversation.id) [多对一]                          │  │  │
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
│  │                            语音通话记录 (VoiceCallRecord)                           │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  - id (PK)                                                                   │  │  │
│  │  │  - call_id (UNIQUE)                                                          │  │  │
│  │  │  - caller_id (FK → User.id) [主叫]                                          │  │  │
│  │  │  - callee_id (FK → User.id) [被叫]                                          │  │  │
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

## 三、实体属性详细说明

### 1. 用户 (User)

**表名**: `auth_user` (Django 内置)

**主键**: `id`

| 属性名 | 类型 | 说明 | 约束 |
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
- 一对多 → Conversation (用户可以创建多个会话)
- 一对一 → UserProfile (用户配置)
- 一对多 → VoiceCallRecord (作为主叫或被叫)

---

### 2. 用户配置 (UserProfile)

**表名**: `chatbot_userprofile`

**主键**: `id`

| 属性名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 配置ID | 主键 |
| user_id | Integer | 用户ID | 外键 → User.id (一对一) |
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
- 一对一 ← User (用户配置属于一个用户)

**说明**:
- 扩展Django内置User模型
- 存储用户的API密钥配置
- 存储用户个性化设置

---

### 3. 会话 (Conversation)

**表名**: `chatbot_conversation`

**主键**: `id`

| 属性名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 会话ID | 主键 |
| user_id | Integer | 用户ID | 外键 → User.id |
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
- 多对一 → User (多个会话属于一个用户)
- 一对多 → Message (一个会话包含多条消息)

**说明**:
- 实现多轮对话的上下文管理
- 通过 `conversation_id` 关联消息
- 记录会话的基本信息和配置

---

### 4. 聊天记录 (Message)

**表名**: `chatbot_message`

**主键**: `id`

| 属性名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 消息ID | 主键 |
| conversation_id | Integer | 会话ID | 外键 → Conversation.id |
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
- 多对一 → Conversation (多条消息属于一个会话)

**说明**:
- 记录用户与AI助手的对话内容
- 支持文本、语音、视频多种消息类型
- 通过 `conversation_id` 实现多轮对话上下文管理

---

### 5. 语音通话记录 (VoiceCallRecord)

**表名**: `chatbot_voicecallrecord`

**主键**: `id`

| 属性名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 通话记录ID | 主键 |
| call_id | String | 通话ID | 唯一 |
| caller_id | Integer | 主叫用户ID | 外键 → User.id |
| callee_id | Integer | 被叫用户ID | 外键 → User.id |
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
- 多对一 → User (主叫用户)
- 多对一 → User (被叫用户)

**说明**:
- 记录语音通话的完整信息
- 支持通话状态追踪
- 存储通话时长和设备信息

---

## 四、E-R 图说明

### 1. 实体关系类型

```
用户 (User) 1 ──< 聊天记录 (Message) N
     │
     │ 1
     ▼
  用户配置 (UserProfile)

用户 (User) 1 ──< 会话 (Conversation) N
     │
     │ 1
     ▼
  语音通话记录 (VoiceCallRecord) N
     │
     │ N (被叫)
     ▼
  用户 (User) 1
```

### 2. 关键关系解释

#### 用户 ↔ 聊天记录 (一对多)
- **一个用户可以有多条聊天记录**
- **一条聊天记录只属于一个用户**
- **外键**: `Message.user_id → User.id`

#### 用户 ↔ 会话 (一对多)
- **一个用户可以创建多个会话**
- **一个会话只属于一个用户**
- **外键**: `Conversation.user_id → User.id`

#### 会话 ↔ 聊天记录 (一对多)
- **一个会话可以包含多条消息**
- **一条消息只属于一个会话**
- **外键**: `Message.conversation_id → Conversation.id`

#### 用户 ↔ 用户配置 (一对一)
- **一个用户只有一个用户配置**
- **一个用户配置只属于一个用户**
- **外键**: `UserProfile.user_id → User.id`

#### 用户 ↔ 语音通话记录 (一对多)
- **一个用户可以发起或接收多通电话**
- **一次通话涉及两个用户（主叫和被叫）**
- **外键**: `VoiceCallRecord.caller_id → User.id`
- **外键**: `VoiceCallRecord.callee_id → User.id`

---

## 五、数据库表结构

### 表关系图

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                              数据库表关系结构图                                           │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  ┌────────────────────┐      ┌────────────────────┐      ┌────────────────────┐          │
│  │   auth_user        │      │  chatbot_profile   │      │ chatbot_conversation │          │
│  ├────────────────────┤      ├────────────────────┤      ├────────────────────┤          │
│  │ id (PK)            │      │ id (PK)            │      │ id (PK)            │          │
│  │ username (UNIQUE)  │      │ user_id (FK)       │      │ user_id (FK)       │          │
│  │ password           │      │ phone              │      │ title              │          │
│  │ email              │      │ avatar             │      │ created_at         │          │
│  │ first_name         │      │ api_keys...        │      │ updated_at         │          │
│  │ last_name          │      │ created_at         │      │ model              │          │
│  │ is_active          │      │ updated_at         │      │ mode               │          │
│  │ is_staff           │      └────────────────────┘      └────────────────────┘          │
│  │ is_superuser       │                                         ▲                          │
│  │ date_joined        │                                         │                          │
│  │ last_login         │                                         │                          │
│  └────────────────────┘                                         │                          │
│         ▲                                                       │                          │
│         │                                                       │                          │
│         │                                                       │                          │
│  ┌──────┴─────────────┐      ┌────────────────────┐      ┌──────┴─────────────┐          │
│  │ chatbot_message    │      │chatbot_voicecall   │      │chatbot_passwordreset │          │
│  ├────────────────────┤      ├────────────────────┤      ├────────────────────┤          │
│  │ id (PK)            │      │ id (PK)            │      │ id (PK)            │          │
│  │ conversation_id(FK)│      │ call_id (UNIQUE)   │      │ user_id (FK)       │          │
│  │ role               │      │ caller_id (FK)     │      │ token              │          │
│  │ message_type       │      │ callee_id (FK)     │      │ created_at         │          │
│  │ content            │      │ status             │      │ expires_at         │          │
│  │ created_at         │      │ initiated_at       │      └────────────────────┘          │
│  │ image_url          │      │ accepted_at        │                                         │
│  │ is_read            │      │ ended_at           │                                         │
│  │ audio_file         │      │ duration           │                                         │
│  │ audio_duration     │      │ caller_device_info │                                         │
│  │ transcription_conf │      │ callee_device_info │                                         │
│  └────────────────────┘      └────────────────────┘                                         │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 六、E-R 图在论文中的应用

### 图 4-3 核心实体 E-R 图

在论文中，可以使用以下格式的E-R图：

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                         图 4-3 核心实体 E-R 图 (Entity-Relationship Diagram)              │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  ┌───────────────┐      1:N       ┌───────────────┐      1:N       ┌───────────────┐       │
│  │    User       │───────────────▶│ Conversation  │───────────────▶│   Message     │       │
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
│                                   │ UserProfile │                                           │
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

1. **User (用户)**: 系统的核心实体，代表系统用户
2. **UserProfile (用户配置)**: 扩展用户信息，存储API密钥等配置
3. **Conversation (会话)**: 实现多轮对话的上下文管理
4. **Message (消息)**: 记录用户与AI助手的对话内容

### 关系说明

- **User ↔ UserProfile**: 一对一关系，每个用户有且仅有一个配置文件
- **User ↔ Conversation**: 一对多关系，一个用户可以创建多个会话
- **Conversation ↔ Message**: 一对多关系，一个会话包含多条消息

---

## 七、总结

本平台的核心实体设计遵循以下原则：

✅ **高内聚**: 每个实体专注于特定功能
✅ **低耦合**: 实体之间通过外键关联，减少直接依赖
✅ **可扩展**: 易于添加新的实体和关系
✅ **规范化**: 符合数据库设计范式

这种设计方式使得系统更加灵活、可维护，并且便于扩展新的功能。
