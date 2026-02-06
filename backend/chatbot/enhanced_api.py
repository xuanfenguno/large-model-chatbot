"""
增强的API调用类，支持模拟响应和API密钥检查
"""
import random
from chatbot.api_base import OpenAIApi, GoogleGeminiApi, MoonshotKimiApi, QwenApi, DeepSeekApi
from django.conf import settings

class EnhancedApiWrapper:
    """增强的API包装器，支持模拟响应和自动模型切换"""
    
    @staticmethod
    def get_available_providers():
        """获取可用的API提供程序"""
        providers = {}
        
        # 检查OpenAI API密钥
        openai_key = getattr(settings, 'OPENAI_API_KEY', None) or settings.LLM_CONFIG.get('OPENAI_API_KEY')
        if openai_key:
            providers['openai'] = openai_key
            
        # 检查Gemini API密钥
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None) or settings.LLM_CONFIG.get('GEMINI_API_KEY')
        if gemini_key:
            providers['gemini'] = gemini_key
            
        # 检查Qwen API密钥
        qwen_key = getattr(settings, 'QWEN_API_KEY', None) or settings.LLM_CONFIG.get('QWEN_API_KEY')
        if qwen_key:
            providers['qwen'] = qwen_key
            
        # 检查Kimi API密钥
        kimi_key = getattr(settings, 'KIMI_API_KEY', None) or settings.LLM_CONFIG.get('KIMI_API_KEY')
        if kimi_key:
            providers['kimi'] = kimi_key
            
        # 检查DeepSeek API密钥
        deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', None) or settings.LLM_CONFIG.get('DEEPSEEK_API_KEY')
        if deepseek_key:
            providers['deepseek'] = deepseek_key
            
        # 检查豆包API密钥
        doubao_key = getattr(settings, 'DOUBAO_API_KEY', None) or settings.LLM_CONFIG.get('DOUBAO_API_KEY')
        if doubao_key:
            providers['doubao'] = doubao_key
            
        return providers
    
    @staticmethod
    def has_any_api_key():
        """检查是否存在任何API密钥"""
        providers = EnhancedApiWrapper.get_available_providers()
        return len(providers) > 0
    
    @staticmethod
    def get_first_available_model():
        """获取第一个可用的模型"""
        providers = EnhancedApiWrapper.get_available_providers()
        
        if 'openai' in providers:
            return 'gpt-3.5-turbo', 'openai'
        elif 'gemini' in providers:
            return 'gemini-pro', 'gemini'
        elif 'qwen' in providers:
            return 'qwen-turbo', 'qwen'
        elif 'deepseek' in providers:
            return 'deepseek-chat', 'deepseek'
        elif 'kimi' in providers:
            return 'kimi-large', 'kimi'
        elif 'doubao' in providers:
            return 'doubao-pro', 'doubao'
        else:
            return None, None

    @staticmethod
    def get_available_models():
        """获取所有可用的模型列表"""
        from .api_base import OpenAIApi, GoogleGeminiApi, MoonshotKimiApi, QwenApi, DeepSeekApi
        all_models = []
        
        # 检查哪些API密钥已配置，仅添加相应模型
        providers = EnhancedApiWrapper.get_available_providers()
        
        if 'openai' in providers:
            all_models.extend(OpenAIApi.get_supported_models())
        if 'gemini' in providers:
            all_models.extend(GoogleGeminiApi.get_supported_models())
        if 'qwen' in providers:
            all_models.extend(QwenApi.get_supported_models())
        if 'deepseek' in providers:
            all_models.extend(DeepSeekApi.get_supported_models())
        if 'kimi' in providers:
            all_models.extend(MoonshotKimiApi.get_supported_models())
        if 'doubao' in providers:
            # 豆包API模型
            all_models.extend([
                {'name': 'doubao-pro', 'label': '豆包Pro'},
                {'name': 'doubao-lite', 'label': '豆包Lite'},
                {'name': 'doubao-ultra', 'label': '豆包Ultra'}
            ])
        
        return all_models

    @staticmethod
    def create_api_instance(model):
        """创建适当的API实例，如果没有API密钥则返回模拟实例"""
        if not EnhancedApiWrapper.has_any_api_key():
            return MockApiInstance()
        
        # 处理无效的模型参数
        if not model or not isinstance(model, str):
            # 如果模型参数无效，默认使用第一个可用的模型
            first_model, provider = EnhancedApiWrapper.get_first_available_model()
            if provider == 'openai':
                return OpenAIApi()
            elif provider == 'gemini':
                return GoogleGeminiApi()
            elif provider == 'qwen':
                return QwenApi()
            elif provider == 'deepseek':
                return DeepSeekApi()
            elif provider == 'kimi':
                return MoonshotKimiApi()
            else:
                return MockApiInstance()
        
        if model.startswith('gpt'):
            # 检查OpenAI API密钥
            api_key = getattr(settings, 'OPENAI_API_KEY', None) or settings.LLM_CONFIG.get('OPENAI_API_KEY')
            if api_key:
                return OpenAIApi()
            else:
                # 返回第一个可用的API实例
                first_model, provider = EnhancedApiWrapper.get_first_available_model()
                if provider == 'openai':
                    return OpenAIApi()
                elif provider == 'gemini':
                    return GoogleGeminiApi()
                elif provider == 'qwen':
                    return QwenApi()
                elif provider == 'deepseek':
                    return DeepSeekApi()
                elif provider == 'kimi':
                    return MoonshotKimiApi()
                else:
                    return MockApiInstance()
        elif model.startswith('gemini'):
            # 检查Gemini API密钥
            api_key = getattr(settings, 'GEMINI_API_KEY', None) or settings.LLM_CONFIG.get('GEMINI_API_KEY')
            if api_key:
                return GoogleGeminiApi()
            else:
                # 返回第一个可用的API实例
                first_model, provider = EnhancedApiWrapper.get_first_available_model()
                if provider == 'gemini':
                    return GoogleGeminiApi()
                elif provider == 'openai':
                    return OpenAIApi()
                elif provider == 'qwen':
                    return QwenApi()
                elif provider == 'deepseek':
                    return DeepSeekApi()
                elif provider == 'kimi':
                    return MoonshotKimiApi()
                else:
                    return MockApiInstance()
        elif model.startswith('kimi'):
            # 检查Kimi API密钥
            api_key = getattr(settings, 'KIMI_API_KEY', None) or settings.LLM_CONFIG.get('KIMI_API_KEY')
            if api_key:
                return MoonshotKimiApi()
            else:
                # 返回第一个可用的API实例
                first_model, provider = EnhancedApiWrapper.get_first_available_model()
                if provider == 'kimi':
                    return MoonshotKimiApi()
                elif provider == 'openai':
                    return OpenAIApi()
                elif provider == 'gemini':
                    return GoogleGeminiApi()
                elif provider == 'qwen':
                    return QwenApi()
                elif provider == 'deepseek':
                    return DeepSeekApi()
                else:
                    return MockApiInstance()
        elif model.startswith('doubao'):
            # 检查豆包API密钥
            api_key = getattr(settings, 'DOUBAO_API_KEY', None) or settings.LLM_CONFIG.get('DOUBAO_API_KEY')
            if api_key:
                return QwenApi()  # 豆包使用类似Qwen的接口
            else:
                # 返回第一个可用的API实例
                first_model, provider = EnhancedApiWrapper.get_first_available_model()
                if provider == 'doubao':
                    return QwenApi()
                elif provider == 'qwen':
                    return QwenApi()
                elif provider == 'openai':
                    return OpenAIApi()
                elif provider == 'gemini':
                    return GoogleGeminiApi()
                elif provider == 'deepseek':
                    return DeepSeekApi()
                elif provider == 'kimi':
                    return MoonshotKimiApi()
                else:
                    return MockApiInstance()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            # 检查Qwen代码API密钥
            code_api_key = getattr(settings, 'QWEN_CODE_API_KEY', None) or settings.LLM_CONFIG.get('QWEN_CODE_API_KEY')
            if code_api_key:
                return QwenApi()
            else:
                qwen_api_key = getattr(settings, 'QWEN_API_KEY', None) or settings.LLM_CONFIG.get('QWEN_API_KEY')
                if qwen_api_key:
                    return QwenApi()
                else:
                    # 返回第一个可用的API实例
                    first_model, provider = EnhancedApiWrapper.get_first_available_model()
                    if provider == 'qwen':
                        return QwenApi()
                    elif provider == 'openai':
                        return OpenAIApi()
                    elif provider == 'gemini':
                        return GoogleGeminiApi()
                    elif provider == 'deepseek':
                        return DeepSeekApi()
                    elif provider == 'kimi':
                        return MoonshotKimiApi()
                    else:
                        return MockApiInstance()
        elif model.startswith('deepseek'):
            # 检查DeepSeek API密钥
            api_key = getattr(settings, 'DEEPSEEK_API_KEY', None) or settings.LLM_CONFIG.get('DEEPSEEK_API_KEY')
            if api_key:
                return DeepSeekApi()
            else:
                # 返回第一个可用的API实例
                first_model, provider = EnhancedApiWrapper.get_first_available_model()
                if provider == 'deepseek':
                    return DeepSeekApi()
                elif provider == 'openai':
                    return OpenAIApi()
                elif provider == 'gemini':
                    return GoogleGeminiApi()
                elif provider == 'qwen':
                    return QwenApi()
                elif provider == 'kimi':
                    return MoonshotKimiApi()
                else:
                    return MockApiInstance()
        elif model.startswith('qwen'):
            # 检查Qwen API密钥
            api_key = getattr(settings, 'QWEN_API_KEY', None) or settings.LLM_CONFIG.get('QWEN_API_KEY')
            if api_key:
                return QwenApi()
            else:
                # 返回第一个可用的API实例
                first_model, provider = EnhancedApiWrapper.get_first_available_model()
                if provider == 'qwen':
                    return QwenApi()
                elif provider == 'openai':
                    return OpenAIApi()
                elif provider == 'gemini':
                    return GoogleGeminiApi()
                elif provider == 'deepseek':
                    return DeepSeekApi()
                elif provider == 'kimi':
                    return MoonshotKimiApi()
                else:
                    return MockApiInstance()
        else:
            # 默认使用OpenAI API
            api_key = getattr(settings, 'OPENAI_API_KEY', None) or settings.LLM_CONFIG.get('OPENAI_API_KEY')
            if api_key:
                return OpenAIApi()
            else:
                # 返回第一个可用的API实例
                first_model, provider = EnhancedApiWrapper.get_first_available_model()
                if provider == 'openai':
                    return OpenAIApi()
                elif provider == 'gemini':
                    return GoogleGeminiApi()
                elif provider == 'qwen':
                    return QwenApi()
                elif provider == 'deepseek':
                    return DeepSeekApi()
                elif provider == 'kimi':
                    return MoonshotKimiApi()
                else:
                    return MockApiInstance()


class MockApiInstance:
    """模拟API实例，用于在没有API密钥时返回模拟响应"""
    
    def __init__(self):
        self.name = "Mock API"
    
    def send_message(self, message, config):
        """返回模拟响应"""
        mock_responses = [
            f"这是来自{self.name}的模拟响应。您输入的是：{message}",
            f"由于未配置API密钥，返回模拟响应。您的问题是：{message}",
            f"系统提示：未配置API密钥，此处显示模拟响应。您询问的是：{message}",
            f"感谢您的提问：{message}。由于缺少API密钥，返回此模拟响应。",
            f"您的输入：{message}。系统当前使用模拟响应，因为没有配置API密钥。"
        ]
        
        import random
        response_text = random.choice(mock_responses)
        
        return {
            'content': response_text,
            'usage': {'prompt_tokens': len(message), 'completion_tokens': len(response_text), 'total_tokens': len(message) + len(response_text)}
        }