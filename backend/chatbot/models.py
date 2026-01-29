from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta

class PasswordResetToken(models.Model):
    """密码重置令牌模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, verbose_name='用户')
    token = models.CharField(max_length=36, unique=True, verbose_name='重置令牌')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(db_index=True, verbose_name='过期时间')
    
    class Meta:
        verbose_name = '密码重置令牌'
        verbose_name_plural = '密码重置令牌'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.token[:8]}...'
    
    @property
    def is_expired(self):
        """检查令牌是否已过期"""
        return datetime.now() > self.expires_at

class Conversation(models.Model):
    """会话模型"""
    
    # 聊天模式选择
    CHAT_MODES = (
        ('text', '文字聊天'),
        ('voice', '语音通话'),
        ('video', '视频通话'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations', db_index=True, verbose_name='用户')
    title = models.CharField(max_length=255, db_index=True, verbose_name='会话标题')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, db_index=True, verbose_name='更新时间')
    model = models.CharField(max_length=50, default='gpt-3.5-turbo', db_index=True, verbose_name='使用的模型')
    mode = models.CharField(max_length=10, choices=CHAT_MODES, default='text', db_index=True, verbose_name='聊天模式')

    class Meta:
        verbose_name = '会话'
        verbose_name_plural = '会话'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

class Message(models.Model):
    """消息模型"""
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

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', db_index=True, verbose_name='会话')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, db_index=True, verbose_name='角色')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text', db_index=True, verbose_name='消息类型')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    image_url = models.URLField(max_length=2000, blank=True, null=True, verbose_name='图片URL')
    is_read = models.BooleanField(default=False, db_index=True, verbose_name='是否已读')
    
    # 语音消息相关字段
    audio_file = models.FileField(upload_to='voice_messages/', blank=True, null=True, verbose_name='语音文件')
    audio_duration = models.FloatField(blank=True, null=True, verbose_name='语音时长(秒)')
    transcription_confidence = models.FloatField(blank=True, null=True, verbose_name='语音识别置信度')

    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}"


class UserProfile(models.Model):
    """用户配置文件，扩展Django内置User模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', db_index=True, verbose_name='用户')
    phone = models.CharField(max_length=15, blank=True, null=True, db_index=True, verbose_name='手机号')
    
    # API密钥配置
    openai_api_key = models.TextField(blank=True, null=True, verbose_name='OpenAI API密钥')
    deepseek_api_key = models.TextField(blank=True, null=True, verbose_name='DeepSeek API密钥')
    qwen_api_key = models.TextField(blank=True, null=True, verbose_name='通义千问API密钥')
    gemini_api_key = models.TextField(blank=True, null=True, verbose_name='Gemini API密钥')
    kimi_api_key = models.TextField(blank=True, null=True, verbose_name='Kimi API密钥')
    doubao_api_key = models.TextField(blank=True, null=True, verbose_name='豆包API密钥')
    qwen_code_api_key = models.TextField(blank=True, null=True, verbose_name='通义千问代码API密钥')
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, db_index=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}的配置"


class VoiceCallRecord(models.Model):
    """语音通话记录模型"""
    STATUS_CHOICES = [
        ('pending', '等待接听'),
        ('accepted', '已接听'),
        ('rejected', '已拒绝'),
        ('ended', '已结束'),
        ('missed', '未接听'),
    ]

    call_id = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='通话ID')
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outgoing_calls', db_index=True, verbose_name='主叫用户')
    callee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incoming_calls', db_index=True, verbose_name='被叫用户')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True, verbose_name='通话状态')
    initiated_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='发起时间')
    accepted_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='接听时间')
    ended_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='结束时间')
    duration = models.IntegerField(default=0, verbose_name='通话时长(秒)')
    caller_device_info = models.JSONField(null=True, blank=True, verbose_name='主叫设备信息')
    callee_device_info = models.JSONField(null=True, blank=True, verbose_name='被叫设备信息')

    class Meta:
        verbose_name = '语音通话记录'
        verbose_name_plural = '语音通话记录'
        ordering = ['-initiated_at']

    def __str__(self):
        return f"{self.caller.username} -> {self.callee.username} ({self.status})"

    @property
    def call_duration(self):
        """计算通话时长"""
        if self.accepted_at and self.ended_at:
            return int((self.ended_at - self.accepted_at).total_seconds())
        return 0


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """创建用户时自动创建用户配置"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存用户时自动保存用户配置"""
    instance.profile.save()