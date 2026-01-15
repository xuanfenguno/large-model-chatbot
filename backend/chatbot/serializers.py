from rest_framework import serializers
from .models import Conversation, Message


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
        fields = ['id', 'title', 'created_at', 'updated_at', 'unread_count', 'last_message']
    
    def get_unread_count(self, obj):
        """获取未读消息数"""
        return obj.messages.filter(role='assistant', is_read=False).count()
    
    def get_last_message(self, obj):
        """获取最后一条消息内容"""
        last_msg = obj.messages.last()
        if last_msg:
            return last_msg.content[:50] if len(last_msg.content) > 50 else last_msg.content
        return ''