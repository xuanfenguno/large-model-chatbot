#!/usr/bin/env python
"""
测试发送消息的脚本
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

def test_send_message():
    """测试发送消息"""
    print("测试发送消息...")
    
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

    # 尝试发送一条消息
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/messages/chat/',
            json={
                'message': '测试消息',
                'model': 'gpt-3.5-turbo'
            },
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=30  # 增加超时时间，因为AI API调用可能较慢
        )
        
        print(f"发送消息API响应状态: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print("✓ 消息发送成功!")
            print(f"响应数据: {result}")
            return True
        else:
            print(f"✗ 消息发送失败，状态码: {response.status_code}")
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
    test_send_message()

if __name__ == "__main__":
    main()