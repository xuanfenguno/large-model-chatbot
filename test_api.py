"""
API功能测试脚本
用于验证后端API的各种功能是否正常工作
"""

import requests
import json

# 服务器地址
BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """测试健康检查API"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health/")
        print(f"Health Check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"Health Check Error: {e}")
        return False

def test_available_models():
    """测试可用模型API"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/models/")
        print(f"Available Models: {response.status_code} - {len(response.json()) if response.status_code == 200 else 'Error'} models")
        return True
    except Exception as e:
        print(f"Available Models Error: {e}")
        return False

def test_login():
    """测试登录功能（使用admin用户）"""
    try:
        payload = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/login/", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Login Success: Token received")
            return data.get('access'), data.get('refresh')
        else:
            print(f"Login Failed: {response.status_code} - {response.json()}")
            return None, None
    except Exception as e:
        print(f"Login Error: {e}")
        return None, None

def test_chat_api(access_token):
    """测试聊天API"""
    if not access_token:
        print("Chat API: No access token, skipping test")
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        payload = {
            "message": "你好，这是一个测试消息",
            "model": "gpt-3.5-turbo"
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat/", json=payload, headers=headers)
        print(f"Chat API: {response.status_code} - {response.json() if response.status_code == 200 else 'Error'}")
    except Exception as e:
        print(f"Chat API Error: {e}")

def main():
    print("开始API功能测试...\n")
    
    # 测试健康检查
    print("1. 测试健康检查API...")
    test_health_check()
    
    # 测试可用模型
    print("\n2. 测试可用模型API...")
    test_available_models()
    
    # 测试登录
    print("\n3. 测试登录功能...")
    access_token, refresh_token = test_login()
    
    # 测试聊天API
    print("\n4. 测试聊天API...")
    test_chat_api(access_token)
    
    print("\nAPI功能测试完成!")

if __name__ == "__main__":
    main()