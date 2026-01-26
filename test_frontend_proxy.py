#!/usr/bin/env python
"""
测试前端代理配置的脚本
这个脚本模拟前端请求通过代理访问后端API
"""
import requests
import json

def test_frontend_proxy():
    """
    测试前端代理是否能正确转发请求到后端API
    """
    print("测试前端代理配置...")
    
    # 前端开发服务器地址
    frontend_base_url = "http://127.0.0.1:8085"
    
    # 测试后端健康检查（通过前端代理）
    try:
        print("\n1. 测试前端代理到后端健康检查API...")
        health_response = requests.get(f"{frontend_base_url}/api/v1/health/")
        print(f"   响应状态码: {health_response.status_code}")
        
        if health_response.status_code == 200:
            print(f"   响应数据: {health_response.json()}")
            print("   ✅ 前端代理健康检查API正常")
        else:
            print(f"   ❌ 健康检查失败，状态码: {health_response.status_code}")
            print(f"   错误内容: {health_response.text}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
    
    # 测试登录API（通过前端代理）
    try:
        print("\n2. 测试前端代理到后端登录API...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        login_response = requests.post(
            f"{frontend_base_url}/api/v1/login/", 
            json=login_data, 
            headers=headers
        )
        
        print(f"   响应状态码: {login_response.status_code}")
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            print(f"   返回字段: {list(response_data.keys())}")
            print("   ✅ 前端代理登录API正常")
            
            # 验证必需的字段
            required_fields = ['access', 'refresh', 'username', 'email']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if not missing_fields:
                print("   ✅ 所有必需字段都存在")
            else:
                print(f"   ⚠️  缺少字段: {missing_fields}")
        else:
            print(f"   ❌ 登录失败，状态码: {login_response.status_code}")
            print(f"   错误内容: {login_response.text}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")

    print("\n" + "="*60)
    print("测试总结:")
    print("- 后端服务器: http://127.0.0.1:8000")
    print("- 前端服务器: http://127.0.0.1:8085")
    print("- 代理配置: /api -> http://127.0.0.1:8000")
    print("- 用户名: admin")
    print("- 密码: admin123")
    print("="*60)

if __name__ == "__main__":
    test_frontend_proxy()