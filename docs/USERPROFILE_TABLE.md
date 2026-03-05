# 系统配置表 (chatbot_userprofile) 详细说明

## 一、表概述

**表名**: `chatbot_userprofile`  
**类型**: 项目自定义表  
**说明**: 扩展用户配置信息，存储用户个性化设置和API密钥，是系统的核心配置表

---

## 二、表结构

| 字段名 | 类型 | 说明 | 约束 | 示例值 |
|-------|------|------|------|--------|
| id | Integer | 配置ID | 主键，自增 | 1 |
| user_id | Integer | 用户ID | 外键，必填，索引 | 1 |
| phone | VARCHAR(15) | 手机号 | 可为空，索引 | "13800138000" |
| avatar | Image | 头像 | 可为空 | "avatars/1.jpg" |
| openai_api_key | Text | OpenAI API密钥 | 可为空 | "sk-..." |
| deepseek_api_key | Text | DeepSeek API密钥 | 可为空 | "sk-..." |
| qwen_api_key | Text | 通义千问API密钥 | 可为空 | "sk-..." |
| gemini_api_key | Text | Gemini API密钥 | 可为空 | "sk-..." |
| kimi_api_key | Text | Kimi API密钥 | 可为空 | "sk-..." |
| doubao_api_key | Text | 豆包API密钥 | 可为空 | "sk-..." |
| qwen_code_api_key | Text | 通义千问代码API密钥 | 可为空 | "sk-..." |
| created_at | DateTime | 创建时间 | 必填，索引 | "2026-01-18 10:00:00" |
| updated_at | DateTime | 更新时间 | 自动更新，索引 | "2026-03-05 15:00:00" |

---

## 三、字段详细说明

### 1. id (配置ID)

- **类型**: Integer (自动递增)
- **约束**: 主键 (Primary Key)
- **说明**: 配置的唯一标识符
- **特点**: 
  - 自动递增
  - 唯一性保证
  - 作为外键关联其他表

### 2. user_id (用户ID)

- **类型**: Integer
- **约束**: 外键，必填 (NOT NULL)，索引 (INDEX)
- **说明**: 关联的用户ID
- **外键**: `user_id → auth_user.id`
- **关系**: 一对一 (一个用户对应一个配置)
- **特点**:
  - Django OneToOneField实现
  - 用户创建时自动创建配置
  - 通过信号量自动管理

### 3. phone (手机号)

- **类型**: VARCHAR(15)
- **约束**: 可为空 (NULL)，索引 (INDEX)
- **说明**: 用户的手机号码
- **特点**:
  - 可选字段
  - 可用于短信验证
  - 可用于找回密码
  - 支持国际号码格式

### 4. avatar (头像)

- **类型**: Image (文件路径)
- **约束**: 可为空 (NULL)
- **说明**: 用户头像
- **上传路径**: `avatars/`
- **默认值**: `"images/person.jpg"`
- **特点**:
  - 可选字段
  - 用于用户界面展示
  - 支持图片格式

### 5. openai_api_key (OpenAI API密钥)

- **类型**: Text (长文本)
- **约束**: 可为空 (NULL)
- **说明**: OpenAI API的API密钥
- **用途**:
  - 调用OpenAI的GPT模型
  - 访问ChatGPT API
  - 使用DALL-E等其他OpenAI服务
- **特点**:
  - 敏感信息，加密存储
  - 可选字段
  - 用户自主配置

### 6. deepseek_api_key (DeepSeek API密钥)

- **类型**: Text (长文本)
- **约束**: 可为空 (NULL)
- **说明**: DeepSeek API的API密钥
- **用途**:
  - 调用DeepSeek的模型
  - 访问DeepSeek API
- **特点**:
  - 敏感信息，加密存储
  - 可选字段
  - 用户自主配置

### 7. qwen_api_key (通义千问API密钥)

- **类型**: Text (长文本)
- **约束**: 可为空 (NULL)
- **说明**: 通义千问API的API密钥
- **用途**:
  - 调用通义千问的模型
  - 访问Qwen API
- **特点**:
  - 敏感信息，加密存储
  - 可选字段
  - 用户自主配置

### 8. gemini_api_key (Gemini API密钥)

- **类型**: Text (长文本)
- **约束**: 可为空 (NULL)
- **说明**: Gemini API的API密钥
- **用途**:
  - 调用Google Gemini模型
  - 访问Gemini API
- **特点**:
  - 敏感信息，加密存储
  - 可选字段
  - 用户自主配置

### 9. kimi_api_key (Kimi API密钥)

- **类型**: Text (长文本)
- **约束**: 可为空 (NULL)
- **说明**: Kimi API的API密钥
- **用途**:
  - 调用Moonshot Kimi模型
  - 访问Kimi API
- **特点**:
  - 敏感信息，加密存储
  - 可选字段
  - 用户自主配置

### 10. doubao_api_key (豆包API密钥)

- **类型**: Text (长文本)
- **约束**: 可为空 (NULL)
- **说明**: 豆包API的API密钥
- **用途**:
  - 调用ByteDance豆包模型
  - 访问Doubao API
- **特点**:
  - 敏感信息，加密存储
  - 可选字段
  - 用户自主配置

### 11. qwen_code_api_key (通义千问代码API密钥)

- **类型**: Text (长文本)
- **约束**: 可为空 (NULL)
- **说明**: 通义千问代码API的API密钥
- **用途**:
  - 调用通义千问代码模型
  - 访问Qwen Code API
  - 代码生成和分析
- **特点**:
  - 敏感信息，加密存储
  - 可选字段
  - 用户自主配置

### 12. created_at (创建时间)

- **类型**: DateTime
- **约束**: 必填 (NOT NULL)，索引 (INDEX)
- **说明**: 配置创建时间
- **特点**:
  - 创建时自动设置
  - 不可修改
  - 用于统计分析

### 13. updated_at (更新时间)

- **类型**: DateTime
- **约束**: 自动更新，索引 (INDEX)
- **说明**: 配置最后更新时间
- **特点**:
  - 每次保存时自动更新
  - 用于显示最后修改时间
  - 用于缓存失效判断

---

## 四、索引说明

### 主键索引
- **字段**: `id`
- **类型**: Primary Key
- **作用**: 唯一标识配置，加速查询

### 外键索引
- **字段**: `user_id`
- **类型**: Foreign Key + Index
- **作用**: 加速用户关联查询

### 普通索引
- **字段**: `phone`
- **类型**: Index
- **作用**: 加速手机号查询

- **字段**: `created_at`
- **类型**: Index
- **作用**: 加速创建时间查询

- **字段**: `updated_at`
- **类型**: Index
- **作用**: 加速更新时间查询

---

## 五、关系说明

### 1. 一对一 → auth_user (用户)

```
chatbot_userprofile (1) ── (1) auth_user
```

- **外键**: `chatbot_userprofile.user_id → auth_user.id`
- **关系**: 一个用户对应一个用户配置
- **实现**: Django OneToOneField
- **特点**:
  - 用户创建时自动创建配置
  - 用户删除时级联删除配置
  - 通过信号量自动管理

---

## 六、Django模型定义

```python
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """用户配置文件，扩展Django内置User模型"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile', 
        db_index=True, 
        verbose_name='用户'
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        db_index=True, 
        verbose_name='手机号'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        default='images/person.jpg', 
        verbose_name='头像'
    )
    
    # API密钥配置
    openai_api_key = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='OpenAI API密钥'
    )
    deepseek_api_key = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='DeepSeek API密钥'
    )
    qwen_api_key = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='通义千问API密钥'
    )
    gemini_api_key = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Gemini API密钥'
    )
    kimi_api_key = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Kimi API密钥'
    )
    doubao_api_key = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='豆包API密钥'
    )
    qwen_code_api_key = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='通义千问代码API密钥'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True, 
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        db_index=True, 
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的配置"

# 信号量：用户创建时自动创建配置
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """创建用户时自动创建用户配置"""
    if created:
        try:
            UserProfile.objects.create(user=instance)
        except IntegrityError:
            # 如果由于并发请求导致重复创建，忽略错误
            pass

# 信号量：用户保存时自动保存配置
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存用户时自动保存用户配置"""
    instance.profile.save()
```

---

## 七、常用操作

### 1. 创建用户配置

```python
from chatbot.models import UserProfile

# 方法1: 通过用户对象创建
user = User.objects.get(id=1)
profile = UserProfile.objects.create(
    user=user,
    phone='13800138000',
    openai_api_key='sk-xxxx'
)

# 方法2: 通过用户对象的profile属性
user = User.objects.get(id=1)
user.profile.phone = '13800138000'
user.profile.openai_api_key = 'sk-xxxx'
user.profile.save()
```

### 2. 查询用户配置

```python
# 按用户ID查询
profile = UserProfile.objects.get(user_id=1)

# 通过用户对象查询
user = User.objects.get(id=1)
profile = user.profile

# 按手机号查询
profiles = UserProfile.objects.filter(phone__contains='138')

# 查询有API密钥的用户
profiles_with_api = UserProfile.objects.exclude(
    openai_api_key__isnull=True
).exclude(openai_api_key__exact='')
```

### 3. 更新用户配置

```python
profile = UserProfile.objects.get(user_id=1)
profile.phone = '13900139000'
profile.openai_api_key = 'sk-newkey'
profile.save()

# 批量更新
UserProfile.objects.filter(user_id=1).update(
    phone='13900139000',
    openai_api_key='sk-newkey'
)
```

### 4. 删除用户配置

```python
profile = UserProfile.objects.get(user_id=1)
profile.delete()
```

### 5. 获取用户配置

```python
# 获取当前用户的配置
def get_user_profile(user):
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    return profile

# 获取用户的API密钥
def get_user_api_key(user, provider):
    profile = user.profile
    if provider == 'openai':
        return profile.openai_api_key
    elif provider == 'deepseek':
        return profile.deepseek_api_key
    # ... 其他provider
```

---

## 八、数据库表结构 (SQL)

```sql
CREATE TABLE chatbot_userprofile (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    phone VARCHAR(15) NULL,
    avatar VARCHAR(100) DEFAULT 'images/person.jpg',
    openai_api_key TEXT NULL,
    deepseek_api_key TEXT NULL,
    qwen_api_key TEXT NULL,
    gemini_api_key TEXT NULL,
    kimi_api_key TEXT NULL,
    doubao_api_key TEXT NULL,
    qwen_code_api_key TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_phone (phone),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at),
    CONSTRAINT fk_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES auth_user(id) 
        ON DELETE CASCADE,
    CONSTRAINT uk_user_id UNIQUE (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 九、数据示例

```sql
INSERT INTO chatbot_userprofile (user_id, phone, avatar, openai_api_key, deepseek_api_key, qwen_api_key, created_at, updated_at) 
VALUES 
(1, '13800138000', 'avatars/1.jpg', 'sk-xxxx', NULL, 'sk-xxxx', '2026-01-18 10:00:00', '2026-03-05 15:00:00'),
(2, '13900139000', 'avatars/2.jpg', NULL, 'sk-xxxx', NULL, '2026-01-20 15:45:00', '2026-03-04 09:15:00'),
(3, NULL, 'images/person.jpg', 'sk-xxxx', 'sk-xxxx', 'sk-xxxx', '2026-01-22 08:30:00', '2026-03-05 14:20:00');
```

---

## 十、使用场景

### 1. API密钥管理

```python
# 获取用户的可用API提供者
def get_available_providers(user):
    profile = user.profile
    providers = []
    
    if profile.openai_api_key:
        providers.append('openai')
    if profile.deepseek_api_key:
        providers.append('deepseek')
    if profile.qwen_api_key:
        providers.append('qwen')
    if profile.gemini_api_key:
        providers.append('gemini')
    if profile.kimi_api_key:
        providers.append('kimi')
    if profile.doubao_api_key:
        providers.append('doubao')
    if profile.qwen_code_api_key:
        providers.append('qwen_code')
    
    return providers

# 检查用户是否有任何API密钥
def has_any_api_key(user):
    profile = user.profile
    return any([
        profile.openai_api_key,
        profile.deepseek_api_key,
        profile.qwen_api_key,
        profile.gemini_api_key,
        profile.kimi_api_key,
        profile.doubao_api_key,
        profile.qwen_code_api_key
    ])
```

### 2. 用户信息展示

```python
# 获取用户完整信息
def get_user_full_info(user):
    profile = user.profile
    return {
        'username': user.username,
        'email': user.email,
        'phone': profile.phone,
        'avatar': profile.avatar.url if profile.avatar else None,
        'created_at': user.date_joined,
        'last_login': user.last_login
    }
```

### 3. 配置更新日志

```python
# 记录配置更新
def log_profile_update(user, field, old_value, new_value):
    UserProfileLog.objects.create(
        user=user,
        field=field,
        old_value=old_value,
        new_value=new_value
    )
```

---

## 十一、最佳实践

### 1. 用户创建时自动配置

```python
# 使用信号量自动创建配置
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            UserProfile.objects.create(user=instance)
        except IntegrityError:
            pass
```

### 2. API密钥安全存储

```python
# 加密存储API密钥
from cryptography.fernet import Fernet

class EncryptedTextField(models.TextField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return self.decrypt(value)
    
    def to_python(self, value):
        if value is None:
            return None
        return self.decrypt(value)
    
    def get_prep_value(self, value):
        if value is None:
            return None
        return self.encrypt(value)
    
    def encrypt(self, value):
        # 实现加密逻辑
        pass
    
    def decrypt(self, value):
        # 实现解密逻辑
        pass
```

### 3. 配置验证

```python
# 验证API密钥格式
def validate_api_key(api_key, provider):
    if not api_key:
        return False, "API密钥不能为空"
    
    if provider == 'openai':
        if not api_key.startswith('sk-'):
            return False, "OpenAI API密钥格式不正确"
    # ... 其他provider验证
    
    return True, "API密钥格式正确"
```

---

## 十二、性能优化

### 1. 缓存优化

```python
from django.core.cache import cache

def get_user_profile_with_cache(user):
    cache_key = f'user_profile_{user.id}'
    profile = cache.get(cache_key)
    
    if profile is None:
        profile = user.profile
        cache.set(cache_key, profile, 3600)  # 缓存1小时
    
    return profile
```

### 2. 数据库查询优化

```python
# 使用select_related优化查询
profile = UserProfile.objects.select_related('user').get(user_id=1)

# 使用only优化查询
profile = UserProfile.objects.only('openai_api_key', 'deepseek_api_key').get(user_id=1)
```

---

## 十三、安全注意事项

### 1. API密钥安全
- ✅ 使用加密存储API密钥
- ✅ 不要在日志中记录API密钥
- ✅ 定期轮换API密钥
- ❌ 不要明文存储API密钥
- ❌ 不要将API密钥提交到Git仓库

### 2. 用户隐私
- ✅ 保护用户手机号
- ✅ 不要随意泄露用户配置
- ✅ 遵守GDPR等隐私法规

### 3. 权限控制
- ✅ 用户只能查看和修改自己的配置
- ✅ 管理员可以查看所有配置
- ❌ 不要泄露其他用户的配置

---

## 十四、总结

chatbot_userprofile表是系统的核心配置表，包含以下特点：

✅ **扩展性**: 扩展Django内置User模型  
✅ **灵活性**: 支持多种API密钥配置  
✅ **个性化**: 存储用户个性化设置  
✅ **安全性**: 敏感信息加密存储  

该表通过一对一关系与User表关联，实现了用户配置的完整管理。
