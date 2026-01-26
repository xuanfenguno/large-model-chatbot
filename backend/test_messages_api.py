#!/usr/bin/env python
"""
测试消息API获取的脚本
"""
import os
import sys
import django
import requests

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from django.contrib.auth.models import User
from chatbot.models import Conversation, Message
from rest_framework_simplejwt.tokens import AccessToken

def test_messages_api():
    """测试消息API获取"""
    print("测试消息API获取...")
    
    # 获取admin用户
    try:
        user = User.objects.get(username='admin')
        print(f"找到用户: {user.username}")
    except User.DoesNotExist:
        print("未找到admin用户")
        return False
    
    # 获取用户的一个会话
    try:
        conversation = Conversation.objects.filter(user=user).first()
        if not conversation:
            print("该用户没有会话，创建一个测试会话...")
            conversation = Conversation.objects.create(
                user=user,
                title="测试会话",
                model="gpt-3.5-turbo"
            )
            print(f"创建测试会话: {conversation.id}")
        else:
            print(f"找到会话: {conversation.id}, 标题: {conversation.title}")
    except Exception as e:
        print(f"获取会话失败: {str(e)}")
        return False
    
    # 生成JWT访问令牌
    access_token = AccessToken.for_user(user)
    print(f"生成访问令牌")
    
    # 尝试通过API获取消息列表
    try:
        response = requests.get(
            f'http://127.0.0.1:8000/api/v1/conversations/{conversation.id}/messages/',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        print(f"API响应状态: {response.status_code}")
        if response.status_code == 200:
            messages = response.json()
            print(f"获取到 {len(messages)} 条消息")
            print("✓ 消息API获取成功!")
            return True
        else:
            print(f"✗ 消息API获取失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"✗ API调用出现异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    test_messages_api()

if __name__ == "__main__":
    main()