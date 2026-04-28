# 数据库 ER 图（实体关系图）

## 一、ER 图

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              数据库 ER 图                                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                            auth_user (Django内置)                             │   │
│  ├──────────────────────────────────────────────────────────────────────────────┤   │
│  │  PK  id                  INT              用户ID                              │   │
│  │      username            VARCHAR(150)     用户名                              │   │
│  │      password            VARCHAR(128)     密码(哈希)                          │   │
│  │      email               VARCHAR(254)     邮箱                                │   │
│  │      first_name          VARCHAR(150)     名                                  │   │
│  │      last_name           VARCHAR(150)     姓                                  │   │
│  │      is_active           BOOLEAN          是否激活                            │   │
│  │      is_staff            BOOLEAN          是否管理员                          │   │
│  │      is_superuser        BOOLEAN          是否超级用户                        │   │
│  │      date_joined         DATETIME         注册时间                            │   │
│  │      last_login          DATETIME         最后登录时间                        │   │
│  └──────────────────────────────┬───────────────────────────────────────────────┘   │
│                                 │ 1                                                 │
│                                 │                                                   │
│                                 │ 1:1                                               │
│                                 │                                                   │
│                                 ▼ 1                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                         chatbot_userprofile                                   │   │
│  ├──────────────────────────────────────────────────────────────────────────────┤   │
│  │  PK  id                  INT              配置ID                              │   │
│  │  FK  user_id             INT              用户ID (1:1)                        │   │
│  │      phone               VARCHAR(15)      手机号                              │   │
│  │      avatar              VARCHAR(100)     头像路径                            │   │
│  │      openai_api_key      TEXT             OpenAI API密钥                      │   │
│  │      deepseek_api_key    TEXT             DeepSeek API密钥                    │   │
│  │      qwen_api_key        TEXT             通义千问API密钥                     │   │
│  │      gemini_api_key      TEXT             Gemini API密钥                      │   │
│  │      kimi_api_key        TEXT             Kimi API密钥                        │   │
│  │      doubao_api_key      TEXT             豆包API密钥                         │   │
│  │      qwen_code_api_key   TEXT             通义千问代码API密钥                 │   │
│  │      theme               VARCHAR(20)      主题模式                            │   │
│  │      language            VARCHAR(10)      语言                                │   │
│  │      save_chat_history   BOOLEAN          保存聊天记录                        │   │
│  │      allow_analytics     BOOLEAN          允许数据统计                        │   │
│  │      created_at          DATETIME         创建时间                            │   │
│  │      updated_at          DATETIME         更新时间                            │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│                                 │ 1                                                 │
│                                 │                                                   │
│                                 │ 1:N                                               │
│                                 │                                                   │
│                                 ▼ N                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                         chatbot_conversation                                  │   │
│  ├──────────────────────────────────────────────────────────────────────────────┤   │
│  │  PK  id                  INT              会话ID                              │   │
│  │  FK  user_id             INT              用户ID (1:N)                        │   │
│  │      title               VARCHAR(255)     会话标题                            │   │
│  │      model               VARCHAR(50)      使用的AI模型                        │   │
│  │      mode                VARCHAR(10)      聊天模式(text/voice/video)          │   │
│  │      created_at          DATETIME         创建时间                            │   │
│  │      updated_at          DATETIME         更新时间                            │   │
│  └──────────────────────────────┬───────────────────────────────────────────────┘   │
│                                 │ 1                                                 │
│                                 │                                                   │
│                                 │ 1:N                                               │
│                                 │                                                   │
│                                 ▼ N                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                         chatbot_message                                       │   │
│  ├──────────────────────────────────────────────────────────────────────────────┤   │
│  │  PK  id                  INT              消息ID                              │   │
│  │  FK  conversation_id     INT              会话ID (1:N)                        │   │
│  │      role                VARCHAR(10)      角色(user/assistant)                │   │
│  │      message_type        VARCHAR(10)      消息类型(text/voice/video)          │   │
│  │      content             TEXT             消息内容                            │   │
│  │      image_url           VARCHAR(2000)    图片URL                             │   │
│  │      audio_file          VARCHAR(100)     语音文件路径                        │   │
│  │      audio_duration      FLOAT            语音时长(秒)                        │   │
│  │      transcription_      FLOAT            语音识别置信度                      │   │
│  │          confidence                                                               │   │
│  │      is_read             BOOLEAN          是否已读                            │   │
│  │      created_at          DATETIME         创建时间                            │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                         chatbot_passwordresettoken                            │   │
│  ├──────────────────────────────────────────────────────────────────────────────┤   │
│  │  PK  id                  INT              令牌ID                              │   │
│  │  FK  user_id             INT              用户ID (N:1)                        │   │
│  │      token               VARCHAR(36)      重置令牌(唯一)                      │   │
│  │      created_at          DATETIME         创建时间                            │   │
│  │      expires_at          DATETIME         过期时间                            │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                         chatbot_voicecallrecord                               │   │
│  ├──────────────────────────────────────────────────────────────────────────────┤   │
│  │  PK  id                  INT              记录ID                              │   │
│  │      call_id             VARCHAR(100)     通话ID(唯一)                        │   │
│  │  FK  caller_id           INT              主叫用户ID (N:1)                    │   │
│  │  FK  callee_id           INT              被叫用户ID (N:1)                    │   │
│  │      status              VARCHAR(20)      通话状态                            │   │
│  │      initiated_at        DATETIME         发起时间                            │   │
│  │      accepted_at         DATETIME         接听时间                            │   │
│  │      ended_at            DATETIME         结束时间                            │   │
│  │      duration            INT              通话时长(秒)                        │   │
│  │      caller_device_info  JSON             主叫设备信息                        │   │
│  │      callee_device_info  JSON             被叫设备信息                        │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 二、实体关系说明

### 1. 实体列表

| 实体名 | 说明 | 对应模型 |
|--------|------|----------|
| `auth_user` | Django 内置用户表 | `User` |
| `chatbot_userprofile` | 用户配置表 | `UserProfile` |
| `chatbot_conversation` | 会话表 | `Conversation` |
| `chatbot_message` | 消息表 | `Message` |
| `chatbot_passwordresettoken` | 密码重置令牌表 | `PasswordResetToken` |
| `chatbot_voicecallrecord` | 语音通话记录表 | `VoiceCallRecord` |

### 2. 关系说明

| 关系 | 类型 | 说明 |
|------|------|------|
| `User` ↔ `UserProfile` | 1:1 | 一个用户对应一个用户配置 |
| `User` ↔ `Conversation` | 1:N | 一个用户可以创建多个会话 |
| `Conversation` ↔ `Message` | 1:N | 一个会话包含多条消息 |
| `User` ↔ `PasswordResetToken` | 1:N | 一个用户可以有多个密码重置令牌 |
| `User` ↔ `VoiceCallRecord` (caller) | 1:N | 一个用户可以发起多个通话 |
| `User` ↔ `VoiceCallRecord` (callee) | 1:N | 一个用户可以接收多个通话 |

## 三、各表详细字段

### 3.1 auth_user（Django 内置用户表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(150) | UNIQUE, NOT NULL | 用户名 |
| password | VARCHAR(128) | NOT NULL | 密码（哈希存储） |
| email | VARCHAR(254) |  | 邮箱地址 |
| first_name | VARCHAR(150) |  | 名 |
| last_name | VARCHAR(150) |  | 姓 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| is_staff | BOOLEAN | DEFAULT FALSE | 是否为管理员 |
| is_superuser | BOOLEAN | DEFAULT FALSE | 是否为超级用户 |
| date_joined | DATETIME | DEFAULT NOW | 注册时间 |
| last_login | DATETIME |  | 最后登录时间 |

### 3.2 chatbot_userprofile（用户配置表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 配置ID |
| user_id | INT | FK → auth_user.id, UNIQUE | 用户ID（1:1关联） |
| phone | VARCHAR(15) |  | 手机号 |
| avatar | VARCHAR(100) | DEFAULT 'images/person.jpg' | 头像路径 |
| openai_api_key | TEXT |  | OpenAI API密钥 |
| deepseek_api_key | TEXT |  | DeepSeek API密钥 |
| qwen_api_key | TEXT |  | 通义千问API密钥 |
| gemini_api_key | TEXT |  | Gemini API密钥 |
| kimi_api_key | TEXT |  | Kimi API密钥 |
| doubao_api_key | TEXT |  | 豆包API密钥 |
| qwen_code_api_key | TEXT |  | 通义千问代码API密钥 |
| theme | VARCHAR(20) | DEFAULT 'auto' | 主题模式 |
| language | VARCHAR(10) | DEFAULT 'zh-CN' | 语言设置 |
| save_chat_history | BOOLEAN | DEFAULT TRUE | 是否保存聊天记录 |
| allow_analytics | BOOLEAN | DEFAULT TRUE | 是否允许数据统计 |
| created_at | DATETIME | AUTO | 创建时间 |
| updated_at | DATETIME | AUTO | 更新时间 |

### 3.3 chatbot_conversation（会话表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 会话ID |
| user_id | INT | FK → auth_user.id | 用户ID |
| title | VARCHAR(255) | NOT NULL | 会话标题 |
| model | VARCHAR(50) | DEFAULT 'gpt-3.5-turbo' | 使用的AI模型 |
| mode | VARCHAR(10) | DEFAULT 'text' | 聊天模式（text/voice/video） |
| created_at | DATETIME | AUTO | 创建时间 |
| updated_at | DATETIME | AUTO | 更新时间 |

**索引**：`user_id`, `title`, `created_at`, `updated_at`, `model`, `mode`

### 3.4 chatbot_message（消息表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 消息ID |
| conversation_id | INT | FK → chatbot_conversation.id | 会话ID |
| role | VARCHAR(10) | NOT NULL | 角色（user/assistant） |
| message_type | VARCHAR(10) | DEFAULT 'text' | 消息类型（text/voice/video） |
| content | TEXT | NOT NULL | 消息内容 |
| image_url | VARCHAR(2000) |  | 图片URL |
| audio_file | VARCHAR(100) |  | 语音文件路径 |
| audio_duration | FLOAT |  | 语音时长（秒） |
| transcription_confidence | FLOAT |  | 语音识别置信度 |
| is_read | BOOLEAN | DEFAULT FALSE | 是否已读 |
| created_at | DATETIME | AUTO | 创建时间 |

**索引**：`conversation_id`, `role`, `message_type`, `created_at`, `is_read`

### 3.5 chatbot_passwordresettoken（密码重置令牌表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 令牌ID |
| user_id | INT | FK → auth_user.id | 用户ID |
| token | VARCHAR(36) | UNIQUE, NOT NULL | 重置令牌（UUID） |
| created_at | DATETIME | AUTO | 创建时间 |
| expires_at | DATETIME | NOT NULL | 过期时间 |

**索引**：`user_id`, `token`, `created_at`, `expires_at`

### 3.6 chatbot_voicecallrecord（语音通话记录表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 记录ID |
| call_id | VARCHAR(100) | UNIQUE, NOT NULL | 通话ID |
| caller_id | INT | FK → auth_user.id | 主叫用户ID |
| callee_id | INT | FK → auth_user.id | 被叫用户ID |
| status | VARCHAR(20) | DEFAULT 'pending' | 通话状态 |
| initiated_at | DATETIME | AUTO | 发起时间 |
| accepted_at | DATETIME |  | 接听时间 |
| ended_at | DATETIME |  | 结束时间 |
| duration | INT | DEFAULT 0 | 通话时长（秒） |
| caller_device_info | JSON |  | 主叫设备信息 |
| callee_device_info | JSON |  | 被叫设备信息 |

**索引**：`call_id`, `caller_id`, `callee_id`, `status`, `initiated_at`, `accepted_at`, `ended_at`

**通话状态枚举**：
- `pending`: 等待接听
- `accepted`: 已接听
- `rejected`: 已拒绝
- `ended`: 已结束
- `missed`: 未接听

## 四、关系图（简化版）

```
auth_user (1) ────── (1) chatbot_userprofile
     │
     │ (1:N)
     │
     ├── (N) chatbot_conversation (1) ────── (N) chatbot_message
     │
     ├── (N) chatbot_passwordresettoken
     │
     ├── (N) chatbot_voicecallrecord (caller_id)
     │
     └── (N) chatbot_voicecallrecord (callee_id)
```

## 五、数据库设计特点

1. **外键约束**：所有关联表都设置了外键约束，保证数据完整性
2. **索引优化**：对常用查询字段（如 `user_id`, `created_at`, `role` 等）建立了索引
3. **级联删除**：当用户删除时，关联的会话、消息、配置等数据会自动删除
4. **软删除支持**：通过 `is_active` 字段支持用户软删除
5. **时间戳追踪**：所有表都包含时间戳字段，便于数据追踪和分析
