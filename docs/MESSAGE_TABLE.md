# 聊天记录表 (chatbot_message) 详细说明

## 一、表概述

**表名**: `chatbot_message`  
**类型**: 项目自定义表  
**说明**: 记录用户与AI助手的对话内容，即"聊天记录"，是系统的核心业务表之一

---

## 二、表结构

| 字段名 | 类型 | 说明 | 约束 | 示例值 |
|-------|------|------|------|--------|
| id | Integer | 消息ID | 主键，自增 | 1 |
| conversation_id | Integer | 会话ID | 外键，必填，索引 | 1 |
| role | VARCHAR(10) | 角色 | 必填，索引 | "user" |
| message_type | VARCHAR(10) | 消息类型 | 默认 'text'，索引 | "text" |
| content | Text | 消息内容 | 必填 | "你好，AI助手" |
| created_at | DateTime | 创建时间 | 必填，索引 | "2026-03-05 14:20:00" |
| image_url | VARCHAR(2000) | 图片URL | 可为空 | "https://..." |
| is_read | Boolean | 是否已读 | 默认 false，索引 | false |
| audio_file | File | 语音文件 | 可为空 | "voice_messages/1.mp3" |
| audio_duration | Float | 语音时长(秒) | 可为空 | 5.5 |
| transcription_confidence | Float | 语音识别置信度 | 可为空 | 0.95 |

---

## 三、字段详细说明

### 1. id (消息ID)

- **类型**: Integer (自动递增)
- **约束**: 主键 (Primary Key)
- **说明**: 消息的唯一标识符
- **特点**: 
  - 自动递增
  - 唯一性保证
  - 作为外键关联其他表

### 2. conversation_id (会话ID)

- **类型**: Integer
- **约束**: 外键，必填 (NOT NULL)，索引 (INDEX)
- **说明**: 关联的会话ID
- **外键**: `conversation_id → chatbot_conversation.id`
- **关系**: 多对一 (多个消息属于一个会话)
- **特点**:
  - 实现多轮对话的上下文管理
  - 通过会话ID组织消息顺序

### 3. role (角色)

- **类型**: VARCHAR(10)
- **约束**: 必填 (NOT NULL)，索引 (INDEX)
- **说明**: 消息发送者的角色
- **取值**:
  - `user` - 用户发送的消息
  - `assistant` - AI助手回复的消息
- **特点**:
  - 区分消息来源
  - 用于消息展示和处理

### 4. message_type (消息类型)

- **类型**: VARCHAR(10)
- **约束**: 默认值 'text'，索引 (INDEX)
- **说明**: 消息的类型
- **取值**:
  - `text` - 文本消息 (默认)
  - `voice` - 语音消息
  - `video` - 视频消息
- **特点**:
  - 支持多种消息类型
  - 用于前端展示不同的消息组件

### 5. content (消息内容)

- **类型**: Text (长文本)
- **约束**: 必填 (NOT NULL)
- **说明**: 消息的具体内容
- **特点**:
  - 可以存储大量文本
  - 支持HTML格式
  - 用于显示给用户

### 6. created_at (创建时间)

- **类型**: DateTime
- **约束**: 必填 (NOT NULL)，索引 (INDEX)
- **说明**: 消息创建时间
- **特点**:
  - 创建时自动设置
  - 用于消息排序
  - 用于统计分析

### 7. image_url (图片URL)

- **类型**: VARCHAR(2000)
- **约束**: 可为空 (NULL)
- **说明**: 图片消息的URL地址
- **特点**:
  - 仅用于图片消息
  - 支持外部图片链接
  - 可为空

### 8. is_read (是否已读)

- **类型**: Boolean
- **约束**: 默认值 false，索引 (INDEX)
- **说明**: 消息是否已被阅读
- **取值**:
  - `true` - 已读
  - `false` - 未读
- **特点**:
  - 用于未读消息提醒
  - 用于消息状态管理

### 9. audio_file (语音文件)

- **类型**: File (文件路径)
- **约束**: 可为空 (NULL)
- **说明**: 语音消息的文件路径
- **上传路径**: `voice_messages/`
- **特点**:
  - 仅用于语音消息
  - 存储音频文件
  - 可为空

### 10. audio_duration (语音时长)

- **类型**: Float
- **约束**: 可为空 (NULL)
- **说明**: 语音消息的时长(秒)
- **特点**:
  - 仅用于语音消息
  - 用于显示语音时长
  - 可为空

### 11. transcription_confidence (语音识别置信度)

- **类型**: Float
- **约束**: 可为空 (NULL)
- **说明**: 语音识别的置信度
- **取值范围**: 0.0 - 1.0
- **特点**:
  - 仅用于语音消息
  - 表示语音识别的准确性
  - 可为空

---

## 四、索引说明

### 主键索引
- **字段**: `id`
- **类型**: Primary Key
- **作用**: 唯一标识消息，加速查询

### 外键索引
- **字段**: `conversation_id`
- **类型**: Foreign Key + Index
- **作用**: 加速会话关联查询

### 普通索引
- **字段**: `role`
- **类型**: Index
- **作用**: 加速角色查询

- **字段**: `message_type`
- **类型**: Index
- **作用**: 加速消息类型查询

- **字段**: `created_at`
- **类型**: Index
- **作用**: 加速时间查询

- **字段**: `is_read`
- **类型**: Index
- **作用**: 加速已读/未读查询

---

## 五、关系说明

### 1. 多对一 → chatbot_conversation (会话)

```
chatbot_message (N) ── (1) chatbot_conversation
```

- **外键**: `chatbot_message.conversation_id → chatbot_conversation.id`
- **关系**: 多条消息属于一个会话
- **实现**: Django ForeignKey
- **作用**: 实现多轮对话的上下文管理

### 2. 多对一 → auth_user (用户)

```
chatbot_message (N) ── (1) auth_user
```

- **间接关联**: 通过 `chatbot_conversation.user_id → auth_user.id`
- **关系**: 多条消息属于一个用户
- **作用**: 查询用户的所有消息

---

## 六、Django模型定义

```python
from django.db import models

class Message(models.Model):
    """消息模型"""
    
    # 角色选择
    ROLE_CHOICES = (
        ('user', '用户'),
        ('assistant', '助手'),
    )
    
    # 消息类型
    MESSAGE_TYPES = (
        ('text', '文本消息'),
        ('voice', '语音消息'),
        ('video', '视频消息'),
    )
    
    conversation = models.ForeignKey(
        'Conversation', 
        on_delete=models.CASCADE, 
        related_name='messages', 
        db_index=True, 
        verbose_name='会话'
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        db_index=True, 
        verbose_name='角色'
    )
    message_type = models.CharField(
        max_length=10, 
        choices=MESSAGE_TYPES, 
        default='text', 
        db_index=True, 
        verbose_name='消息类型'
    )
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True, 
        verbose_name='创建时间'
    )
    image_url = models.URLField(
        max_length=2000, 
        blank=True, 
        null=True, 
        verbose_name='图片URL'
    )
    is_read = models.BooleanField(
        default=False, 
        db_index=True, 
        verbose_name='是否已读'
    )
    audio_file = models.FileField(
        upload_to='voice_messages/', 
        blank=True, 
        null=True, 
        verbose_name='语音文件'
    )
    audio_duration = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name='语音时长(秒)'
    )
    transcription_confidence = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name='语音识别置信度'
    )
    
    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}"
```

---

## 七、常用操作

### 1. 创建消息

```python
from chatbot.models import Message

# 创建用户消息
message = Message.objects.create(
    conversation_id=1,
    role='user',
    message_type='text',
    content='你好，AI助手',
    is_read=False
)

# 创建助手回复消息
message = Message.objects.create(
    conversation_id=1,
    role='assistant',
    message_type='text',
    content='你好！有什么可以帮助你的？',
    is_read=False
)
```

### 2. 查询消息

```python
# 按ID查询
message = Message.objects.get(id=1)

# 按会话查询
messages = Message.objects.filter(conversation_id=1)

# 按角色查询
user_messages = Message.objects.filter(role='user')
assistant_messages = Message.objects.filter(role='assistant')

# 按消息类型查询
text_messages = Message.objects.filter(message_type='text')
voice_messages = Message.objects.filter(message_type='voice')

# 查询未读消息
unread_messages = Message.objects.filter(is_read=False)

# 按时间范围查询
from datetime import datetime, timedelta
start_time = datetime.now() - timedelta(days=1)
end_messages = Message.objects.filter(created_at__gte=start_time)

# 按会话查询并排序
messages = Message.objects.filter(conversation_id=1).order_by('created_at')

# 查询会话的最后一条消息
last_message = Message.objects.filter(conversation_id=1).last()
```

### 3. 更新消息

```python
message = Message.objects.get(id=1)
message.is_read = True
message.save()

# 批量更新
Message.objects.filter(conversation_id=1).update(is_read=True)
```

### 4. 删除消息

```python
# 删除单条消息
message = Message.objects.get(id=1)
message.delete()

# 删除会话的所有消息
Message.objects.filter(conversation_id=1).delete()
```

### 5. 统计消息

```python
# 统计会话的消息数量
message_count = Message.objects.filter(conversation_id=1).count()

# 统计用户的总消息数
from chatbot.models import Conversation
user_messages = Message.objects.filter(
    conversation__user_id=1
).count()

# 统计未读消息数
unread_count = Message.objects.filter(is_read=False).count()
```

---

## 八、数据库表结构 (SQL)

```sql
CREATE TABLE chatbot_message (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    role VARCHAR(10) NOT NULL,
    message_type VARCHAR(10) NOT NULL DEFAULT 'text',
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    image_url VARCHAR(2000) NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    audio_file VARCHAR(100) NULL,
    audio_duration FLOAT NULL,
    transcription_confidence FLOAT NULL,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_role (role),
    INDEX idx_message_type (message_type),
    INDEX idx_created_at (created_at),
    INDEX idx_is_read (is_read),
    CONSTRAINT fk_conversation_id 
        FOREIGN KEY (conversation_id) 
        REFERENCES chatbot_conversation(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 九、数据示例

```sql
-- 用户发送的消息
INSERT INTO chatbot_message (conversation_id, role, message_type, content, created_at, is_read) 
VALUES 
(1, 'user', 'text', '你好，AI助手', '2026-03-05 14:20:00', FALSE),
(1, 'user', 'text', '你能帮我写一篇论文吗', '2026-03-05 14:21:00', FALSE);

-- 助手回复的消息
INSERT INTO chatbot_message (conversation_id, role, message_type, content, created_at, is_read) 
VALUES 
(1, 'assistant', 'text', '你好！有什么可以帮助你的？', '2026-03-05 14:20:05', FALSE),
(1, 'assistant', 'text', '当然可以！请告诉我你的论文主题和要求。', '2026-03-05 14:21:10', FALSE);

-- 语音消息
INSERT INTO chatbot_message (conversation_id, role, message_type, content, created_at, audio_file, audio_duration, transcription_confidence) 
VALUES 
(1, 'user', 'voice', '语音内容转文字', '2026-03-05 14:22:00', 'voice_messages/1.mp3', 5.5, 0.95);
```

---

## 十、使用场景

### 1. 多轮对话管理

```python
# 获取会话的所有消息
def get_conversation_messages(conversation_id):
    messages = Message.objects.filter(
        conversation_id=conversation_id
    ).order_by('created_at')
    return messages

# 示例输出:
# 1. user: 你好
# 2. assistant: 你好！有什么可以帮助你的？
# 3. user: 我需要写一篇论文
# 4. assistant: 请告诉我论文主题和要求
```

### 2. 消息历史记录

```python
# 获取用户的所有消息历史
def get_user_message_history(user_id):
    messages = Message.objects.filter(
        conversation__user_id=user_id
    ).order_by('-created_at')[:100]
    return messages
```

### 3. 未读消息统计

```python
# 统计未读消息数
def get_unread_count(user_id):
    return Message.objects.filter(
        conversation__user_id=user_id,
        is_read=False
    ).count()
```

### 4. 消息统计分析

```python
# 统计每日消息数量
from django.db.models import Count
from django.db.models.functions import TruncDate

daily_messages = Message.objects.annotate(
    date=TruncDate('created_at')
).values('date').annotate(
    count=Count('id')
).order_by('-date')
```

---

## 十一、最佳实践

### 1. 消息创建

```python
# 在视图中创建消息
def create_message(request):
    conversation_id = request.data.get('conversation_id')
    role = request.data.get('role')
    content = request.data.get('content')
    
    message = Message.objects.create(
        conversation_id=conversation_id,
        role=role,
        message_type='text',
        content=content
    )
    
    return Response({'message_id': message.id})
```

### 2. 消息查询优化

```python
# 使用select_related优化查询
messages = Message.objects.filter(
    conversation_id=1
).select_related(
    'conversation'
).order_by('created_at')

# 使用prefetch_related优化查询
conversations = Conversation.objects.filter(
    user_id=1
).prefetch_related(
    'messages'
)
```

### 3. 批量操作

```python
# 批量标记为已读
Message.objects.filter(
    conversation_id=1,
    is_read=False
).update(is_read=True)
```

---

## 十二、性能优化

### 1. 索引优化

```sql
-- 确保以下索引存在
CREATE INDEX idx_conversation_created ON chatbot_message (conversation_id, created_at);
CREATE INDEX idx_user_created ON chatbot_message (conversation_id, created_at) 
WHERE conversation_id IN (SELECT id FROM chatbot_conversation WHERE user_id = ?);
```

### 2. 分页查询

```python
# 分页查询消息
from django.core.paginator import Paginator

def get_messages_with_pagination(conversation_id, page=1, page_size=20):
    messages = Message.objects.filter(
        conversation_id=conversation_id
    ).order_by('created_at')
    
    paginator = Paginator(messages, page_size)
    page_obj = paginator.get_page(page)
    
    return page_obj
```

---

## 十三、安全注意事项

### 1. 内容安全
- ✅ 过滤用户输入内容
- ✅ 防止XSS攻击
- ✅ 防止SQL注入
- ❌ 不要直接执行用户输入的代码

### 2. 权限控制
- ✅ 确保用户只能访问自己的消息
- ✅ 管理员可以查看所有消息
- ❌ 不要泄露其他用户的消息

### 3. 数据备份
- ✅ 定期备份消息数据
- ✅ 异地备份
- ✅ 版本控制

---

## 十四、总结

chatbot_message表是系统的核心业务表，包含以下特点：

✅ **完整性**: 包含消息的所有信息  
✅ **多样性**: 支持多种消息类型  
✅ **可追溯**: 通过会话ID实现多轮对话管理  
✅ **可扩展**: 支持语音、视频等多媒体消息  

该表与chatbot_conversation表配合，实现了完整的聊天功能。
