#!/usr/bin/env python
"""
测试前端实际使用场景的脚本
模拟前端发送消息和获取响应的完整流程
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

def test_frontend_workflow():
    """测试前端实际工作流程"""
    print("=== 测试前端实际工作流程 ===")
    
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
            json={'title': '前端测试会话'},
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

    # 2. 发送消息到该会话
    print(f"\n2. 向会话 {conversation_id} 发送消息...")
    try:
        response = requests.post(
            f'http://127.0.0.1:8000/api/v1/conversations/{conversation_id}/send_message/',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json={
                'message': '前端测试消息',
                'model': 'gpt-4'
            },
            timeout=30  # 给AI响应更多时间
        )
        
        if response.status_code == 200:
            message_data = response.json()
            print(f"✓ 发送消息成功")
            print(f"  用户消息: {message_data.get('user_message', {}).get('content', 'N/A')}")
            print(f"  AI回复: {message_data.get('assistant_message', 'N/A')[:50]}...")
        elif response.status_code == 206:  # 部分内容返回
            message_data = response.json()
            print(f"! 收到部分内容 (状态码 206)")
            print(f"  用户消息: {message_data.get('user_message', {}).get('content', 'N/A')}")
            print(f"  AI回复: {message_data.get('assistant_message', 'N/A')[:50]}...")
        else:
            print(f"✗ 发送消息失败，状态码: {response.status_code}")
            print(f"错误: {response.text}")
            # 尝试获取更详细的错误信息
            try:
                error_detail = response.json()
                print(f"详细错误: {error_detail}")
            except:
                pass
            return False
    except requests.exceptions.Timeout:
        print("! 请求超时 - AI服务响应时间过长")
        print("  这可能是网络问题或API密钥无效")
    except Exception as e:
        print(f"✗ 发送消息时出现异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # 3. 获取该会话的所有消息
    print(f"\n3. 获取会话 {conversation_id} 的所有消息...")
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

    # 4. 获取所有会话列表
    print(f"\n4. 获取所有会话列表...")
    try:
        response = requests.get(
            'http://127.0.0.1:8000/api/v1/conversations/',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"✓ 获取到 {len(conversations)} 个会话")
            for conv in conversations:
                print(f"  - 会话ID {conv['id']}: {conv['title']} (更新于 {conv['updated_at']})")
        else:
            print(f"✗ 获取会话列表失败，状态码: {response.status_code}")
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 获取会话列表时出现异常: {str(e)}")
        return False

    print(f"\n✓ 完整前端工作流程测试完成!")
    return True

def main():
    test_frontend_workflow()

if __name__ == "__main__":
    main()