from rest_framework import serializers
from django.contrib.auth.models import User
from app.models.models import Conversation, Message, PasswordResetToken, UserProfile


class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at', 'image_url', 'is_read']
        read_only_fields = ['id', 'created_at', 'is_read']


class ConversationSerializer(serializers.ModelSerializer):
    """会话序列化器"""
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'unread_count', 'last_message', 'model']  # 添加model字段
    
    def get_unread_count(self, obj):
        """获取未读消息数"""
        return obj.messages.filter(role='assistant', is_read=False).count()
    
    def get_last_message(self, obj):
        """获取最后一条消息内容"""
        last_msg = obj.messages.last()
        if last_msg:
            return last_msg.content[:50] if len(last_msg.content) > 50 else last_msg.content
        return ''


class PasswordResetTokenSerializer(serializers.ModelSerializer):
    """密码重置令牌序列化器"""
    
    class Meta:
        model = PasswordResetToken
        fields = ['id', 'user', 'token', 'created_at', 'expires_at', 'is_expired']
        read_only_fields = ['id', 'created_at', 'is_expired']


class UserProfileSerializer(serializers.ModelSerializer):
    """用户配置序列化器"""
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'avatar', 
                 'openai_api_key', 'deepseek_api_key', 'qwen_api_key', 
                 'gemini_api_key', 'kimi_api_key', 'doubao_api_key', 'qwen_code_api_key']
        extra_kwargs = {
            'openai_api_key': {'write_only': True},
            'deepseek_api_key': {'write_only': True},
            'qwen_api_key': {'write_only': True},
            'gemini_api_key': {'write_only': True},
            'kimi_api_key': {'write_only': True},
            'doubao_api_key': {'write_only': True},
            'qwen_code_api_key': {'write_only': True},
        }
    
    def get_avatar(self, obj):
        """返回头像的完整URL"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器（包含配置信息）"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']