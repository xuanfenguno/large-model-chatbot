#!/usr/bin/env python
"""
测试修复后的消息发送功能
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

def test_send_message_fix():
    """测试修复后的消息发送功能"""
    print("=== 测试修复后的消息发送功能 ===")
    
    # 获取admin用户
    try:
        user = User.objects.get(username='admin')
        print(f"✓ 找到用户: {user.username}")
    except User.DoesNotExist:
        print("✗ 未找到admin用户")
        return False

    # 生成JWT访问令牌
    access_token = AccessToken.for_user(user)
    print(f"✓ 生成访问令牌")

    # 1. 创建一个新会话
    print("\n1. 创建新会话...")
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/conversations/',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json={'title': '修复后测试会话'},
            timeout=10
        )
        
        if response.status_code == 201:
            conversation_data = response.json()
            conversation_id = conversation_data['id']
            print(f"✓ 创建会话成功，ID: {conversation_id}")
        else:
            print(f"✗ 创建会话失败，状态码: {response.status_code}")
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 创建会话时出现异常: {str(e)}")
        return False

    # 2. 向该会话发送用户消息（模拟前端行为）
    print(f"\n2. 向会话 {conversation_id} 发送用户消息...")
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/messages/',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json={
                'conversation_id': conversation_id,
                'role': 'user',
                'content': '修复后测试消息'
            },
            timeout=10
        )
        
        if response.status_code == 201:
            message_data = response.json()
            user_message_id = message_data['id']
            print(f"✓ 用户消息发送成功，ID: {user_message_id}")
        else:
            print(f"✗ 用户消息发送失败，状态码: {response.status_code}")
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 发送用户消息时出现异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # 3. 向该会话发送AI助手消息（模拟前端行为）
    print(f"\n3. 向会话 {conversation_id} 发送AI助手消息...")
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/messages/',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json={
                'conversation_id': conversation_id,
                'role': 'assistant',
                'content': 'AI助手回复测试'
            },
            timeout=10
        )
        
        if response.status_code == 201:
            message_data = response.json()
            ai_message_id = message_data['id']
            print(f"✓ AI助手消息发送成功，ID: {ai_message_id}")
        else:
            print(f"✗ AI助手消息发送失败，状态码: {response.status_code}")
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 发送AI助手消息时出现异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # 4. 获取该会话的所有消息
    print(f"\n4. 获取会话 {conversation_id} 的所有消息...")
    try:
        response = requests.get(
            f'http://127.0.0.1:8000/api/v1/conversations/{conversation_id}/messages/',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✓ 获取到 {len(messages)} 条消息")
            for i, msg in enumerate(messages):
                print(f"  [{i+1}] [{msg['role']}] {msg['content'][:50]}...")
        else:
            print(f"✗ 获取消息失败，状态码: {response.status_code}")
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 获取消息时出现异常: {str(e)}")
        return False

    print(f"\n✓ 消息发送功能修复测试完成!")
    print("现在前端应该能够正常发送消息并保存到对应会话中。")
    return True

def main():
    test_send_message_fix()

if __name__ == "__main__":
    main()