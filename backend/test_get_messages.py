#!/usr/bin/env python
"""
测试获取特定会话消息的脚本
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

def test_get_messages():
    """测试获取特定会话的消息"""
    print("测试获取特定会话的消息...")
    
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

    # 测试获取会话32的消息
    try:
        response = requests.get(
            'http://127.0.0.1:8000/api/v1/conversations/32/messages/',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        print(f"获取会话32的消息，状态码: {response.status_code}")
        if response.status_code == 200:
            messages = response.json()
            print(f"获取到 {len(messages)} 条消息")
            for msg in messages:
                print(f"  - [{msg['role']}] {msg['content'][:50]}...")
            print("✓ 获取会话消息成功!")
            return True
        else:
            print(f"✗ 获取会话消息失败，状态码: {response.status_code}")
            print(f"错误: {response.text}")
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
    test_get_messages()

if __name__ == "__main__":
    main()