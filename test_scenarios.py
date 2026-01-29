"""
测试function_router API不同场景的脚本
"""
import os
import sys
import django
import json
import urllib.request
import urllib.parse
import traceback
import time

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def test_various_scenarios():
    print("=== 测试各种场景下的function_router API ===")
    
    base_url = 'http://127.0.0.1:10001/api/v1/function-router/'
    
    test_cases = [
        {"input": "你好", "model": "qwen-turbo"},
        {"input": "讲个笑话", "model": "qwen-turbo"},
        {"input": "计算1+1", "model": "qwen-turbo"},
        {"input": "天气如何", "model": "qwen-turbo"},
        {"input": "你好", "model": "gpt-3.5-turbo"},
        {"input": "你好", "model": "gemini-pro"},
        {"input": "", "model": "qwen-turbo"},  # 测试空输入
        {"input": "这是一个很长的测试输入" * 100, "model": "qwen-turbo"},  # 测试长输入
    ]
    
    for i, test_data in enumerate(test_cases):
        print(f"\n--- 测试案例 {i+1}: {test_data['input'][:30]}{'...' if len(test_data['input']) > 30 else ''} ---")
        try:
            req = urllib.request.Request(base_url, 
                                       data=json.dumps(test_data).encode('utf-8'),
                                       headers={
                                           'Content-Type': 'application/json',
                                           'User-Agent': 'Mozilla/5.0'
                                       })
            
            print(f"请求数据: {json.dumps(test_data, ensure_ascii=False)}")
            
            response = urllib.request.urlopen(req, timeout=30)
            result = response.read().decode('utf-8')
            
            print(f"状态码: {response.getcode()}")
            print(f"响应: {result}")
            
        except urllib.error.HTTPError as e:
            print(f"HTTP错误: {e.code} - {e.reason}")
            error_content = e.read().decode('utf-8')
            print(f"错误响应: {error_content}")
        except Exception as e:
            print(f"其他错误: {str(e)}")
            traceback.print_exc()
        
        # 等待一段时间避免过于频繁的请求
        time.sleep(1)

if __name__ == "__main__":
    test_various_scenarios()