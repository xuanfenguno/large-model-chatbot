"""
测试function_router功能的脚本
"""
import os
import sys
import django
import json
import urllib.request
import urllib.parse

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def test_function_router_api():
    print("=== 测试function_router API ===")
    
    try:
        # 测试function_router接口
        url = 'http://127.0.0.1:10001/api/v1/function-router/'
        
        # 准备测试数据
        test_data = {
            "input": "你好",
            "model": "qwen-turbo"
        }
        
        # 发送POST请求
        req = urllib.request.Request(url, 
                                   data=json.dumps(test_data).encode('utf-8'),
                                   headers={
                                       'Content-Type': 'application/json',
                                       'User-Agent': 'Mozilla/5.0'
                                   })
        
        response = urllib.request.urlopen(req, timeout=30)
        result = response.read().decode('utf-8')
        
        print(f"状态码: {response.getcode()}")
        print(f"响应: {result}")
        
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code} - {e.reason}")
        print(f"错误响应: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"URL错误: {e.reason}")
    except Exception as e:
        print(f"其他错误: {str(e)}")

if __name__ == "__main__":
    test_function_router_api()