from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta

class PasswordResetToken(models.Model):
    """密码重置令牌模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    token = models.CharField(max_length=36, unique=True, verbose_name='重置令牌')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations', verbose_name='用户')
    title = models.CharField(max_length=255, verbose_name='会话标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    model = models.CharField(max_length=50, default='gpt-3.5-turbo', verbose_name='使用的模型')
    mode = models.CharField(max_length=10, choices=CHAT_MODES, default='text', verbose_name='聊天模式')

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

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name='会话')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='角色')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    image_url = models.URLField(max_length=2000, blank=True, null=True, verbose_name='图片URL')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='手机号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}的配置"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """创建用户时自动创建用户配置"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存用户时自动保存用户配置"""
    instance.profile.save()