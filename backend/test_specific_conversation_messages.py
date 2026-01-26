#!/usr/bin/env python
"""
测试特定会话的消息API获取的脚本
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
from rest_framework_simplejwt.tokens import AccessToken

def test_specific_conversation_messages():
    """测试特定会话的消息API获取"""
    print("测试特定会话的消息API获取...")
    
    # 获取admin用户
    try:
        user = User.objects.get(username='admin')
        print(f"找到用户: {user.username}")
    except User.DoesNotExist:
        print("未找到admin用户")
        return False

    # 生成JWT访问令牌
    access_token = AccessToken.for_user(user)
    print(f"生成访问令牌")

    # 尝试获取第一个会话的消息（使用ID 31）
    try:
        response = requests.get(
            'http://127.0.0.1:8000/api/v1/conversations/31/messages/',
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
            for msg in messages:
                print(f"  - 角色: {msg['role']}, 内容: {msg['content'][:50]}...")
            print("✓ 特定会话消息API获取成功!")
            return True
        else:
            print(f"✗ 特定会话消息API获取失败，状态码: {response.status_code}")
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
    test_specific_conversation_messages()

if __name__ == "__main__":
    main()