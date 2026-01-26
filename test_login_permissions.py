#!/usr/bin/env python
"""
专门测试登录API权限的脚本
"""
import requests
import json

def test_login_permissions():
    """
    测试登录API是否允许未经认证的用户访问
    """
    print("测试登录API权限设置...")
    
    # 测试后端直接访问
    backend_url = "http://127.0.0.1:8000/api/v1/login/"
    frontend_proxy_url = "http://127.0.0.1:8085/api/v1/login/"
    
    test_cases = [
        ("后端直接访问", backend_url),
        ("前端代理访问", frontend_proxy_url)
    ]
    
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Test Client)'
    }
    
    for name, url in test_cases:
        print(f"\n--- {name}: {url} ---")
        try:
            response = requests.post(url, json=login_data, headers=headers, timeout=10)
            
            print(f"  状态码: {response.status_code}")
            print(f"  响应头: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                print(f"  响应JSON: {json.dumps(response_json, ensure_ascii=False)[:200]}...")
                
                # 检查是否成功登录
                if response.status_code == 200:
                    expected_fields = ['access', 'refresh', 'username', 'email']
                    success = all(field in response_json for field in expected_fields)
                    print(f"  ✅ 登录成功: {success}")
                elif response.status_code == 401:
                    print(f"  ❌ 需要认证: 可能是全局权限设置影响了登录端点")
                elif response.status_code == 403:
                    print(f"  ❌ 权限被拒绝")
                else:
                    print(f"  ⚠️  其他状态码: {response.status_code}")
            except:
                print(f"  ❌ 响应不是JSON格式: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 请求异常: {e}")

    print("\n" + "="*60)
    print("权限测试完成")
    print("注意: 登录端点应该允许未经认证的用户访问")
    print("如果返回401或403，可能是装饰器没有正确覆盖全局权限设置")
    print("="*60)

if __name__ == "__main__":
    test_login_permissions()