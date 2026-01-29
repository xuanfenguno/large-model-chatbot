"""
测试可能引起500错误的场景
"""
import json
import urllib.request

def test_error_scenarios():
    print("=== 测试可能的错误场景 ===")
    
    base_url = 'http://127.0.0.1:10001/api/v1/function-router/'
    
    # 测试可能导致错误的场景
    error_test_cases = [
        {"input": "你好", "model": ""},  # 空模型
        {"input": "你好", "model": "nonexistent-model"},  # 不存在的模型
        {"input": "你好", "model": None},  # None模型
        {"input": "你好"},  # 缺少模型参数
        {},  # 空请求体
        {"input": "你好", "model": "qwen-turbo", "extra_param": "extra_value"},  # 额外参数
    ]
    
    for i, test_data in enumerate(error_test_cases):
        print(f"\n--- 错误测试案例 {i+1}: {test_data} ---")
        try:
            req = urllib.request.Request(base_url, 
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
            error_content = e.read().decode('utf-8')
            print(f"错误响应: {error_content}")
        except Exception as e:
            print(f"其他错误: {str(e)}")

if __name__ == "__main__":
    test_error_scenarios()