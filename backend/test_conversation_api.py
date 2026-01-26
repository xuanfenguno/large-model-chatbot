#!/usr/bin/env python
"""
测试会话API创建的脚本
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
from chatbot.models import Conversation
from rest_framework_simplejwt.tokens import AccessToken

def test_conversation_api():
    """测试会话API创建"""
    print("测试会话API创建...")
    
    # 获取admin用户
    try:
        user = User.objects.get(username='admin')
        print(f"找到用户: {user.username}")
    except User.DoesNotExist:
        print("未找到admin用户，创建测试用户...")
        user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print(f"创建超级用户: {user.username}")
    
    # 生成JWT访问令牌
    access_token = AccessToken.for_user(user)
    print(f"生成访问令牌: {access_token}")
    
    # 尝试通过API创建会话
    try:
        # 注意：这里使用实际的API端点
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/conversations/',
            json={'title': '通过API创建的测试会话'},
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        print(f"API响应状态: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
        if response.status_code == 201:
            print("✓ 会话API创建成功!")
            return True
        else:
            print(f"✗ 会话API创建失败，状态码: {response.status_code}")
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
    test_conversation_api()

if __name__ == "__main__":
    main()