#!/usr/bin/env python
"""
前端登录流程调试脚本
模拟真实的浏览器登录行为
"""
import requests
import json

def simulate_browser_login():
    """
    模拟浏览器行为进行登录测试
    """
    print("模拟浏览器登录流程...")
    
    # 使用Session来保持Cookie等状态
    session = requests.Session()
    
    # 设置浏览器头部
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Origin': 'http://127.0.0.1:8085',
        'Referer': 'http://127.0.0.1:8085/',
    }
    
    frontend_url = "http://127.0.0.1:8085"
    
    print(f"1. 访问前端主页: {frontend_url}")
    try:
        home_response = session.get(frontend_url, timeout=10)
        print(f"   主页状态码: {home_response.status_code}")
    except Exception as e:
        print(f"   访问主页失败: {e}")
    
    print(f"\n2. 尝试登录...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    # 添加CORS相关的头部
    login_headers = headers.copy()
    login_headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    })
    
    try:
        login_response = session.post(
            f"{frontend_url}/api/v1/login/",
            json=login_data,
            headers=login_headers,
            timeout=10
        )
        
        print(f"   登录响应状态码: {login_response.status_code}")
        print(f"   登录响应头: {dict(login_response.headers)}")
        
        try:
            response_data = login_response.json()
            print(f"   登录响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)[:500]}...")
            
            if login_response.status_code == 200:
                print("   ✅ 登录API调用成功")
                
                # 检查响应数据结构
                required_fields = ['access', 'refresh', 'username', 'email']
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if not missing_fields:
                    print("   ✅ 所有必需字段都存在")
                    
                    # 检查token是否正确
                    access_token = response_data.get('access')
                    if access_token and len(access_token) > 50:  # JWT tokens are typically long
                        print(f"   ✅ 访问令牌格式正确 (长度: {len(access_token)})")
                    else:
                        print(f"   ⚠️  访问令牌可能有问题: {access_token}")
                        
                else:
                    print(f"   ❌ 缺少必需字段: {missing_fields}")
            else:
                print(f"   ❌ 登录API调用失败")
                print(f"   错误详情: {response_data}")
                
        except ValueError:
            print(f"   ❌ 响应不是JSON格式: {login_response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ 登录请求失败: {e}")
    
    print(f"\n3. 测试使用获取的token访问受保护的API...")
    # 如果前面的登录成功，尝试使用token访问需要认证的API
    if login_response.status_code == 200:
        try:
            response_data = login_response.json()
            access_token = response_data.get('access')
            
            if access_token:
                protected_headers = headers.copy()
                protected_headers['Authorization'] = f'Bearer {access_token}'
                
                protected_response = session.get(
                    f"{frontend_url}/api/v1/models/",
                    headers=protected_headers,
                    timeout=10
                )
                
                print(f"   受保护API状态码: {protected_response.status_code}")
                
                if protected_response.status_code == 200:
                    print("   ✅ 使用token访问受保护API成功")
                elif protected_response.status_code == 401:
                    print("   ❌ 使用token访问受保护API失败 - 认证失败")
                else:
                    print(f"   ⚠️  受保护API返回其他状态码: {protected_response.status_code}")
            else:
                print("   ❌ 无法获取访问令牌，跳过受保护API测试")
                
        except Exception as e:
            print(f"   ❌ 受保护API测试失败: {e}")
    
    print("\n" + "="*60)
    print("浏览器登录模拟完成")
    print("如果API层面正常但前端仍显示登录失败，")
    print("问题可能出现在前端JavaScript代码中")
    print("="*60)

if __name__ == "__main__":
    simulate_browser_login()