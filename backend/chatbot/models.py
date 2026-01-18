from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Conversation(models.Model):
    """会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations', verbose_name='用户')
    title = models.CharField(max_length=255, verbose_name='会话标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    model = models.CharField(max_length=50, default='gpt-3.5-turbo', verbose_name='使用的模型')  # 添加模型字段

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

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name='会话')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='角色')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    image_url = models.URLField(max_length=2000, blank=True, null=True, verbose_name='图片URL')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')

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