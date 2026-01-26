#!/usr/bin/env python
"""
调试会话创建问题的脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from django.contrib.auth.models import User
from chatbot.models import Conversation, UserProfile
from django.db import transaction

def debug_conversation_creation():
    """调试会话创建过程"""
    print("开始调试会话创建过程...")
    
    # 尝试获取一个用户（例如admin用户）
    try:
        user = User.objects.get(username='admin')
        print(f"找到用户: {user.username}")
    except User.DoesNotExist:
        print("未找到admin用户，尝试创建一个测试用户...")
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        print(f"创建测试用户: {user.username}")
    
    # 检查用户是否有配置文件
    try:
        profile = user.profile
        print(f"用户配置文件存在: {profile}")
    except UserProfile.DoesNotExist:
        print("用户配置文件不存在，创建配置文件...")
        profile = UserProfile.objects.create(user=user)
        print(f"创建配置文件: {profile}")
    
    # 尝试创建会话
    try:
        print("尝试创建会话...")
        conversation = Conversation.objects.create(
            user=user,
            title="测试会话",
            model="gpt-3.5-turbo"
        )
        print(f"会话创建成功! ID: {conversation.id}, 标题: {conversation.title}")
        
        # 验证会话是否正确保存
        saved_conv = Conversation.objects.get(id=conversation.id)
        print(f"验证保存的会话: {saved_conv.title} by {saved_conv.user.username}")
        
    except Exception as e:
        print(f"会话创建失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    debug_conversation_creation()

if __name__ == "__main__":
    main()