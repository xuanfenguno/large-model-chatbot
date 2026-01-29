"""
测试Qwen API配置是否正确的脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from django.conf import settings
from chatbot.enhanced_api import EnhancedApiWrapper
from chatbot.api_base import QwenApi

def test_qwen_api():
    print("=== Qwen API 测试 ===")
    
    # 检查环境变量
    print(f"环境变量 QWEN_API_KEY: {os.getenv('QWEN_API_KEY', 'NOT SET')[:20]}...")
    print(f"环境变量 QWEN_API_BASE_URL: {os.getenv('QWEN_API_BASE_URL', 'NOT SET')}")
    
    # 检查Django settings
    print(f"Settings QWEN_API_KEY: {getattr(settings, 'QWEN_API_KEY', 'NOT SET')}")
    print(f"Settings LLM_CONFIG QWEN_API_KEY: {settings.LLM_CONFIG.get('QWEN_API_KEY', 'NOT SET')}")
    
    # 直接检查settings.LLM_CONFIG
    print(f"Settings LLM_CONFIG keys: {list(settings.LLM_CONFIG.keys())}")
    
    # 检查EnhancedApiWrapper是否能识别Qwen API
    providers = EnhancedApiWrapper.get_available_providers()
    print(f"可用API提供者: {providers}")
    
    # 测试EnhancedApiWrapper创建Qwen实例
    api_instance = EnhancedApiWrapper.create_api_instance('qwen-turbo')
    print(f"创建的API实例类型: {type(api_instance).__name__}")
    
    if isinstance(api_instance, QwenApi):
        print("✓ EnhancedApiWrapper 正确创建了 QwenApi 实例")
    else:
        print("✗ EnhancedApiWrapper 没有创建 QwenApi 实例")
        
    # 检查是否有任何API密钥
    has_any = EnhancedApiWrapper.has_any_api_key()
    print(f"是否有任何API密钥: {has_any}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_qwen_api()