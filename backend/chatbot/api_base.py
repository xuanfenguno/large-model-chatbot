"""
API调用基类，用于封装公共的大模型API调用逻辑
"""
import requests
import json
import logging
from django.conf import settings
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class BaseAIApi:
    """大模型API调用基类"""
    
    def __init__(self):
        self.base_url = ""
        self.headers = {}
        self.name = "BaseAI"
    
    def _prepare_headers(self, api_key: str) -> Dict[str, str]:
        """准备请求头"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    
    def _prepare_payload(self, message: str, history: List[Dict], config: Dict) -> Dict:
        """准备请求载荷"""
        # 构建消息历史，最多保留8条
        messages = self._build_messages(message, history)
        
        payload = {
            'messages': messages,
            'temperature': config.get('temperature', 0.6),
            'max_tokens': config.get('max_tokens', 2000),
            'top_p': config.get('top_p', 0.7),
        }
        
        # 添加模型特定的参数
        model = config.get('model')
        if model:
            payload['model'] = model
            
        return payload
    
    def _build_messages(self, user_message: str, history: List[Dict]) -> List[Dict]:
        """构建消息历史"""
        messages = []
        
        # 添加历史消息，最多保留8条
        if history:
            messages.extend(history[-8:])
        
        # 添加当前用户消息
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        return messages
    
    def _make_request(self, url: str, headers: Dict, payload: Dict, timeout: int = 30) -> Dict:
        """执行HTTP请求"""
        try:
            response = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            if not response.ok:
                logger.error(f"{self.name} API请求失败: {response.status_code} - {response.text}")
                raise Exception(f"{self.name} API错误: {response.status_code}")
            
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"{self.name} API请求超时")
            raise Exception(f"{self.name} API请求超时")
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.name} API请求异常: {str(e)}")
            raise Exception(f"{self.name} API请求异常: {str(e)}")
        except json.JSONDecodeError:
            logger.error(f"{self.name} API响应JSON解析失败")
            raise Exception(f"{self.name} API响应解析失败")
    
    def _validate_config(self, config: Dict) -> None:
        """验证配置参数"""
        required_params = ['model']
        for param in required_params:
            if not config.get(param):
                raise ValueError(f"缺少必需参数: {param}")
        
        temperature = config.get('temperature', 0.6)
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            raise ValueError("温度参数必须在0-2之间")
        
        max_tokens = config.get('max_tokens', 2000)
        if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 4000:
            raise ValueError("最大token数必须在1-4000之间")

    def _extract_response_content(self, response_data: Dict) -> Dict:
        """从API响应中提取内容，子类需要实现具体的提取逻辑"""
        raise NotImplementedError("子类必须实现_extract_response_content方法")
    
    def send_message(self, message: str, config: Dict) -> Dict:
        """发送消息到AI模型"""
        # 验证配置
        self._validate_config(config)
        
        # 获取API密钥
        api_key = self._get_api_key(config.get('model'))
        if not api_key:
            raise Exception(f"未配置{self.name} API密钥")
        
        # 准备请求参数
        headers = self._prepare_headers(api_key)
        payload = self._prepare_payload(
            message=message,
            history=config.get('history', []),
            config=config
        )
        
        # 发送请求
        response_data = self._make_request(
            url=self.base_url,
            headers=headers,
            payload=payload,
            timeout=config.get('timeout', 30)
        )
        
        # 提取响应内容
        return self._extract_response_content(response_data)
    
    def _get_api_key(self, model: str) -> Optional[str]:
        """获取对应的API密钥，子类需要实现"""
        raise NotImplementedError("子类必须实现_get_api_key方法")


class OpenAIApi(BaseAIApi):
    """OpenAI API实现"""
    
    def __init__(self):
        super().__init__()
        self.base_url = getattr(settings, 'OPENAI_API_BASE_URL', 'https://api.openai.com/v1/chat/completions')
        self.name = "OpenAI"
    
    def _get_api_key(self, model: str) -> Optional[str]:
        return getattr(settings, 'OPENAI_API_KEY', None)
    
    def _prepare_headers(self, api_key: str) -> Dict[str, str]:
        """准备OpenAI API请求头"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    
    def _prepare_payload(self, message: str, history: List[Dict], config: Dict) -> Dict:
        """准备OpenAI API请求载荷"""
        # 构建消息历史
        messages = self._build_messages(message, history)
        
        payload = {
            'model': config.get('model', 'gpt-3.5-turbo'),
            'messages': messages,
            'temperature': config.get('temperature', 0.6),
            'max_tokens': config.get('max_tokens', 2000),
            'top_p': config.get('top_p', 0.7),
        }
        
        return payload
    
    def _extract_response_content(self, response_data: Dict) -> Dict:
        """从OpenAI API响应中提取内容"""
        if 'choices' not in response_data or len(response_data['choices']) == 0:
            raise Exception("OpenAI API响应格式错误")
        
        content = response_data['choices'][0]['message']['content']
        
        usage = response_data.get('usage', {})
        
        return {
            'content': content,
            'usage': usage
        }


class GoogleGeminiApi(BaseAIApi):
    """Google Gemini API实现"""
    
    def __init__(self):
        super().__init__()
        self.name = "Google Gemini"
    
    def _get_api_key(self, model: str) -> Optional[str]:
        return getattr(settings, 'GEMINI_API_KEY', None)
    
    def send_message(self, message: str, config: Dict) -> Dict:
        """重写发送消息方法以适配Gemini API格式"""
        # 验证配置
        self._validate_config(config)
        
        # 获取API密钥
        api_key = self._get_api_key(config.get('model'))
        if not api_key:
            raise Exception(f"未配置{self.name} API密钥")
        
        # 构建Gemini API格式的消息
        messages = self._build_gemini_messages(message, config.get('history', []))
        
        # 准备请求参数
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.get('model')}:generateContent?key={api_key}"
        
        payload = {
            'contents': messages,
            'generationConfig': {
                'temperature': config.get('temperature', 0.6),
                'maxOutputTokens': config.get('max_tokens', 2000),
                'topP': config.get('top_p', 0.7),
            }
        }
        
        # 发送请求
        response_data = self._make_request(
            url=url,
            headers={'Content-Type': 'application/json'},
            payload=payload,
            timeout=config.get('timeout', 30)
        )
        
        # 提取响应内容
        return self._extract_response_content(response_data)
    
    def _build_gemini_messages(self, user_message: str, history: List[Dict]) -> List[Dict]:
        """构建Gemini API格式的消息"""
        messages = []
        
        # 处理历史消息
        if history:
            for msg in history[-8:]:  # 最多保留8条历史
                role = 'user' if msg['role'] in ['user', 'human'] else 'model'
                messages.append({
                    'role': role,
                    'parts': [{'text': msg['content']}]
                })
        
        # 添加当前用户消息
        messages.append({
            'role': 'user',
            'parts': [{'text': user_message}]
        })
        
        return messages
    
    def _extract_response_content(self, response_data: Dict) -> Dict:
        """从Gemini API响应中提取内容"""
        if 'candidates' not in response_data or len(response_data['candidates']) == 0:
            raise Exception("Gemini API响应格式错误")
        
        content_parts = response_data['candidates'][0]['content']['parts']
        content = ''.join([part.get('text', '') for part in content_parts])
        
        # Gemini API可能不返回usage信息
        usage = response_data.get('usageMetadata', {})
        
        return {
            'content': content,
            'usage': usage
        }


class MoonshotKimiApi(BaseAIApi):
    """Moonshot Kimi API实现"""
    
    def __init__(self):
        super().__init__()
        self.base_url = getattr(settings, 'MOONSHOT_API_BASE_URL', 'https://api.moonshot.cn/v1')
        self.name = "Moonshot Kimi"
    
    def _get_api_key(self, model: str) -> Optional[str]:
        return getattr(settings, 'MOONSHOT_API_KEY', None)
    
    def _prepare_payload(self, message: str, history: List[Dict], config: Dict) -> Dict:
        """准备OpenAI兼容的请求载荷"""
        # 构建消息历史
        messages = self._build_messages(message, history)
        
        payload = {
            'model': config.get('model', 'moonshot-v1-8k'),
            'messages': messages,
            'temperature': config.get('temperature', 0.6),
            'max_tokens': config.get('max_tokens', 2000),
            'top_p': config.get('top_p', 0.7),
        }
        
        return payload
    
    def _extract_response_content(self, response_data: Dict) -> Dict:
        """从OpenAI兼容响应中提取内容"""
        if 'choices' not in response_data or len(response_data['choices']) == 0:
            raise Exception("Moonshot API响应格式错误")
        
        content = response_data['choices'][0]['message']['content']
        
        usage = response_data.get('usage', {})
        
        return {
            'content': content,
            'usage': usage
        }


class DoubaoApi(BaseAIApi):
    """字节跳动豆包API实现"""
    
    def __init__(self):
        super().__init__()
        self.name = "Doubao"
    
    def _get_api_key(self, model: str) -> Optional[str]:
        # 豆包API通常使用不同的认证方式，这里简化处理
        return getattr(settings, 'DOUBAO_API_KEY', None)
    
    def send_message(self, message: str, config: Dict) -> Dict:
        """重写发送消息方法以适配豆包API格式"""
        # 豆包API的具体实现会根据实际API文档调整
        # 这里提供一个通用模板
        raise NotImplementedError("豆包API的具体实现需要根据官方文档调整")


class QwenApi(BaseAIApi):
    """通义千问API实现 - OpenAI兼容接口"""
    
    def __init__(self):
        super().__init__()
        self.base_url = getattr(settings, 'QWEN_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.name = "Qwen"
    
    def _get_api_key(self, model: str) -> Optional[str]:
        return getattr(settings, 'QWEN_API_KEY', None)
    
    def _prepare_headers(self, api_key: str) -> Dict[str, str]:
        """使用标准的OpenAI API头部格式"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    
    def _prepare_payload(self, message: str, history: List[Dict], config: Dict) -> Dict:
        """准备OpenAI兼容的请求载荷"""
        # 构建消息历史
        messages = self._build_messages(message, history)
        
        payload = {
            'model': config.get('model', 'qwen-turbo'),
            'messages': messages,
            'temperature': config.get('temperature', 0.6),
            'max_tokens': config.get('max_tokens', 2000),
            'top_p': config.get('top_p', 0.7),
        }
        
        return payload
    
    def _extract_response_content(self, response_data: Dict) -> Dict:
        """从OpenAI兼容响应中提取内容"""
        if 'choices' not in response_data or len(response_data['choices']) == 0:
            raise Exception("Qwen API响应格式错误")
        
        content = response_data['choices'][0]['message']['content']
        
        usage = response_data.get('usage', {})
        
        return {
            'content': content,
            'usage': usage
        }


class DeepSeekApi(BaseAIApi):
    """DeepSeek API实现 - OpenAI兼容接口"""
    
    def __init__(self):
        super().__init__()
        self.base_url = getattr(settings, 'DEEPSEEK_API_BASE_URL', 'https://api.deepseek.com/v1')
        self.name = "DeepSeek"
    
    def _get_api_key(self, model: str) -> Optional[str]:
        return getattr(settings, 'DEEPSEEK_API_KEY', None)
    
    def _prepare_payload(self, message: str, history: List[Dict], config: Dict) -> Dict:
        """准备OpenAI兼容的请求载荷"""
        # 构建消息历史
        messages = self._build_messages(message, history)
        
        payload = {
            'model': config.get('model', 'deepseek-chat'),
            'messages': messages,
            'temperature': config.get('temperature', 0.6),
            'max_tokens': config.get('max_tokens', 2000),
            'top_p': config.get('top_p', 0.7),
        }
        
        return payload
    
    def _extract_response_content(self, response_data: Dict) -> Dict:
        """从OpenAI兼容响应中提取内容"""
        if 'choices' not in response_data or len(response_data['choices']) == 0:
            raise Exception("DeepSeek API响应格式错误")
        
        content = response_data['choices'][0]['message']['content']
        
        usage = response_data.get('usage', {})
        
        return {
            'content': content,
            'usage': usage
        }