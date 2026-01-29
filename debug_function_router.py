"""
详细测试function_router功能的脚本
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

django.setup()

from chatbot.function_router import FunctionRouter
from chatbot.enhanced_api import EnhancedApiWrapper

def test_function_router_directly():
    print("=== 直接测试FunctionRouter ===")
    
    try:
        # 直接测试FunctionRouter
        router = FunctionRouter()
        
        # 测试路由功能
        result = router.route_function("你好", "qwen-turbo")
        print(f"FunctionRouter结果: {result}")
        
    except Exception as e:
        print(f"FunctionRouter错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_enhanced_api_wrapper():
    print("\n=== 测试EnhancedApiWrapper ===")
    
    try:
        # 测试EnhancedApiWrapper
        api_instance = EnhancedApiWrapper.create_api_instance('qwen-turbo')
        print(f"API实例类型: {type(api_instance).__name__}")
        
        if hasattr(api_instance, 'send_message'):
            # 尝试发送一个简单消息
            config = {
                'model': 'qwen-turbo',
                'temperature': 0.7,
                'max_tokens': 200,
                'top_p': 0.8,
                'history': []
            }
            result = api_instance.send_message("你好", config)
            print(f"API调用结果: {result}")
        else:
            print("API实例没有send_message方法")
        
    except Exception as e:
        print(f"EnhancedApiWrapper错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_api_key_access():
    print("\n=== 测试API密钥访问 ===")
    
    from django.conf import settings
    print(f"settings.LLM_CONFIG['QWEN_API_KEY']: {settings.LLM_CONFIG.get('QWEN_API_KEY', 'NOT FOUND')[:20]}...")
    
    # 测试get_available_providers
    providers = EnhancedApiWrapper.get_available_providers()
    print(f"可用提供商: {providers}")

if __name__ == "__main__":
    test_api_key_access()
    test_enhanced_api_wrapper()
    test_function_router_directly()