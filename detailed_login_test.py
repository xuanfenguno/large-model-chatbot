#!/usr/bin/env python
"""
详细测试前端登录过程的脚本
"""
import requests
import json
import time

def detailed_login_test():
    """
    详细测试前端登录流程
    """
    print("详细测试前端登录流程...")
    
    # 前端开发服务器地址
    frontend_base_url = "http://127.0.0.1:8085"
    
    print(f"\n测试目标: {frontend_base_url}")
    print("用户名: admin")
    print("密码: admin123")
    
    # 测试各种API端点
    endpoints_to_test = [
        "/api/v1/health/",
        "/api/v1/login/",
        "/api/v1/models/"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n--- 测试端点: {endpoint} ---")
        try:
            if endpoint == "/api/v1/login/":
                # 登录用POST请求
                login_data = {
                    'username': 'admin',
                    'password': 'admin123'
                }
                
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.post(
                    f"{frontend_base_url}{endpoint}", 
                    json=login_data, 
                    headers=headers,
                    timeout=10
                )
            else:
                # 其他端点用GET请求
                headers = {
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(
                    f"{frontend_base_url}{endpoint}",
                    headers=headers,
                    timeout=10
                )
            
            print(f"  状态码: {response.status_code}")
            print(f"  响应头: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                print(f"  响应JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            except:
                print(f"  响应文本: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ 连接错误: {e}")
        except requests.exceptions.Timeout as e:
            print(f"  ❌ 请求超时: {e}")
        except Exception as e:
            print(f"  ❌ 请求异常: {e}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("如果登录仍然失败，请检查以下几点：")
    print("1. 浏览器控制台是否有错误信息")
    print("2. 是否清除了浏览器缓存")
    print("3. 是否使用了正确的用户名密码：admin/admin123")
    print("4. 前端页面是否已刷新")
    print("="*60)

if __name__ == "__main__":
    detailed_login_test()