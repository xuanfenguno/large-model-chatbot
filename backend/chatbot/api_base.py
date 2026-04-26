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
    
    def _build_messages(self, user_message, history: List[Dict]) -> List[Dict]:
        """构建消息历史，支持多模态内容"""
        messages = []

        # 添加系统消息，强制使用Markdown格式
        messages.append({
            'role': 'system',
            'content': 'You are a helpful assistant. Please format your response in Markdown.'
        })
        
        # 添加历史消息，最多保留8条
        if history:
            messages.extend(history[-8:])
        
        # 添加当前用户消息（支持文本或多模态内容）
        if isinstance(user_message, list):
            # 多模态消息（包含图片）
            messages.append({
                'role': 'user',
                'content': user_message
            })
        else:
            # 纯文本消息
            messages.append({
                'role': 'user',
                'content': user_message
            })
        
        return messages
    
    def _make_request(self, url: str, headers: Dict, payload: Dict, timeout: int = 15) -> Dict:
        """执行HTTP请求 - 优化：减少默认超时时间"""
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
        
        # 构建请求URL
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        
        # 发送请求 - 优化：减少默认超时时间到15秒
        response_data = self._make_request(
            url=url,
            headers=headers,
            payload=payload,
            timeout=config.get('timeout', 15)
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
    
    @staticmethod
    def get_supported_models():
        return [
            {'name': 'gpt-4', 'label': 'GPT-4'},
            {'name': 'gpt-4-32k', 'label': 'GPT-4-32k'},
            {'name': 'gpt-4-turbo', 'label': 'GPT-4 Turbo'},
            {'name': 'gpt-3.5-turbo', 'label': 'GPT-3.5 Turbo'},
        ]
    
    def _get_api_key(self, model: str) -> Optional[str]:
        return getattr(settings, 'OPENAI_API_KEY', None) or settings.LLM_CONFIG.get('OPENAI_API_KEY')
    
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

    @staticmethod
    def get_supported_models():
        return [
            {'name': 'gemini-pro', 'label': 'Gemini Pro'},
        ]
    """Google Gemini API实现"""
    
    def __init__(self):
        super().__init__()
        self.name = "Google Gemini"
    
    def _get_api_key(self, model: str) -> Optional[str]:
        return getattr(settings, 'GEMINI_API_KEY', None) or settings.LLM_CONFIG.get('GEMINI_API_KEY')
    
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

    @staticmethod
    def get_supported_models():
        return [
            {'name': 'moonshot-v1-8k', 'label': 'Moonshot V1 8K'},
            {'name': 'moonshot-v1-32k', 'label': 'Moonshot V1 32K'},
            {'name': 'moonshot-v1-128k', 'label': 'Moonshot V1 128K'},
        ]
    
    def _get_api_key(self, model: str) -> Optional[str]:
        return getattr(settings, 'MOONSHOT_API_KEY', None) or settings.LLM_CONFIG.get('KIMI_API_KEY')
    
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
        return getattr(settings, 'DOUBAO_API_KEY', None) or settings.LLM_CONFIG.get('DOUBAO_API_KEY')
    
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
        return getattr(settings, 'QWEN_API_KEY', None) or settings.LLM_CONFIG.get('QWEN_API_KEY')

    @staticmethod
    def get_supported_models():
        return [
            # 多模态模型
            {'id': 'qwen-vl-plus', 'name': 'Qwen VL Plus (支持图片)', 'provider': 'Qwen', 'available': True, 'group': '多模态'},
            {'id': 'qwen-vl-max', 'name': 'Qwen VL Max (支持图片)', 'provider': 'Qwen', 'available': True, 'group': '多模态'},
            {'id': 'gpt-4o', 'name': 'GPT-4o', 'provider': 'OpenAI', 'available': False, 'group': '多模态'},
            {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'provider': 'Google', 'available': False, 'group': '多模态'},
            # 高性能模型
            {'id': 'qwen-max', 'name': 'Qwen Max', 'provider': 'Qwen', 'available': True, 'group': '高性能'},
            {'id': 'gpt-4', 'name': 'GPT-4', 'provider': 'OpenAI', 'available': False, 'group': '高性能'},
            {'id': 'claude-3-opus', 'name': 'Claude 3 Opus', 'provider': 'Anthropic', 'available': False, 'group': '高性能'},
            # 通用模型
            {'id': 'qwen-turbo', 'name': 'Qwen Turbo', 'provider': 'Qwen', 'available': True, 'group': '通用'},
            {'id': 'qwen-plus', 'name': 'Qwen Plus', 'provider': 'Qwen', 'available': True, 'group': '通用'},
            {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'provider': 'OpenAI', 'available': False, 'group': '通用'},
            {'id': 'claude-3-sonnet', 'name': 'Claude 3 Sonnet', 'provider': 'Anthropic', 'available': False, 'group': '通用'},
            {'id': 'gemini-pro', 'name': 'Gemini Pro', 'provider': 'Google', 'available': False, 'group': '通用'},
            {'id': 'deepseek-chat', 'name': 'DeepSeek Chat', 'provider': 'DeepSeek', 'available': False, 'group': '通用'},
            # 开源模型
            {'id': 'llama-3-70b', 'name': 'Llama 3 70B', 'provider': 'Meta', 'available': False, 'group': '开源'},
            {'id': 'mistral-large', 'name': 'Mistral Large', 'provider': 'Mistral', 'available': False, 'group': '开源'}
        ]
    
    def send_message(self, message: str, config: Dict, image_url: Optional[str] = None) -> Dict:
        """重写发送消息方法以适配Qwen API格式"""
        # 验证配置
        self._validate_config(config)
        
        # 获取API密钥
        api_key = self._get_api_key(config.get('model'))
        if not api_key:
            raise Exception(f"未配置{self.name} API密钥")
        
        # 处理图片URL
        if image_url:
            # 构建多模态消息格式
            multimodal_message = [
                {
                    "type": "text",
                    "text": message
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
            message = multimodal_message
        
        # 准备请求参数
        headers = self._prepare_headers(api_key)
        payload = self._prepare_payload(
            message=message,
            history=config.get('history', []),
            config=config
        )
        
        # 对于OpenAI兼容API，需要在基础URL后添加/chat/completions端点
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        
        # 发送请求 - 优化：减少默认超时时间到15秒
        response_data = self._make_request(
            url=url,
            headers=headers,
            payload=payload,
            timeout=config.get('timeout', 15)
        )
        
        # 提取响应内容
        return self._extract_response_content(response_data)
    
    def send_message_stream(self, message: str, config: Dict):
        """流式发送消息，逐块返回响应"""
        # 验证配置
        self._validate_config(config)
        
        # 获取API密钥
        api_key = self._get_api_key(config.get('model'))
        if not api_key:
            raise Exception(f"未配置{self.name} API密钥")
        
        # 准备请求参数
        headers = self._prepare_headers(api_key)
        
        # 确保启用流式模式
        config['stream'] = True
        
        payload = self._prepare_payload(
            message=message,
            history=config.get('history', []),
            config=config
        )
        
        # 对于OpenAI兼容API，需要在基础URL后添加/chat/completions端点
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        
        # 发送流式请求
        try:
            response = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=(5, 30),  # 优化：连接超时5秒，读取超时30秒
                stream=True  # 启用流式响应
            )
            
            if not response.ok:
                logger.error(f"{self.name} API请求失败: {response.status_code} - {response.text}")
                raise Exception(f"{self.name} API错误: {response.status_code}")
            
            # 逐块读取SSE响应
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            # 提取内容块
                            if data.get('choices') and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
            
        except requests.exceptions.Timeout:
            logger.error(f"{self.name} API请求超时")
            raise Exception(f"{self.name} API请求超时")
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.name} API请求异常: {str(e)}")
            raise Exception(f"{self.name} API请求异常: {str(e)}")
    
    def _prepare_headers(self, api_key: str) -> Dict[str, str]:
        """使用标准的OpenAI API头部格式"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    
    def _prepare_payload(self, message, history: List[Dict], config: Dict) -> Dict:
        """准备Qwen API的请求载荷 - 支持原生和兼容模式，支持多模态"""
        model = config.get('model', 'qwen-turbo')
        
        # 检查是否使用视觉模型
        is_vision_model = 'vl' in model.lower()
        
        # 检查是否使用DashScope兼容模式 (包含'compatible-mode'的是兼容模式)
        if 'dashscope.aliyuncs.com' in self.base_url and 'compatible-mode' in self.base_url:
            # OpenAI兼容格式
            messages = []
            
            # 添加系统消息
            messages.append({
                'role': 'system',
                'content': 'You are a helpful assistant. Please format your response in Markdown.'
            })
            
            # 添加历史消息
            if history:
                messages.extend(history[-8:])  # 最多保留8条历史记录
            
            # 添加当前用户消息（支持多模态内容）
            if isinstance(message, list):
                # 多模态消息（包含图片）
                messages.append({
                    'role': 'user',
                    'content': message
                })
            else:
                # 纯文本消息
                messages.append({
                    'role': 'user',
                    'content': message
                })
            
            payload = {
                'model': model,
                'messages': messages,
                'temperature': config.get('temperature', 0.6),
                'max_tokens': config.get('max_tokens', 2000),
                'top_p': config.get('top_p', 0.7),
                'stream': config.get('stream', False),  # 支持流式输出
            }
            
            # 视觉模型需要额外的参数
            if is_vision_model:
                # 如果是HTTP URL，需要下载并转换为Base64
                # 因为Qwen API服务器无法访问127.0.0.1这种本地地址
                for msg in payload.get('messages', []):
                    if isinstance(msg.get('content'), list):
                        for item in msg['content']:
                            if item.get('type') == 'image_url':
                                image_url = item.get('image_url', {}).get('url', '')
                                if image_url and image_url.startswith('http'):
                                    base64_url = self._convert_image_to_base64(image_url)
                                    if base64_url:
                                        item['image_url']['url'] = base64_url
            
            return payload

    def _convert_image_to_base64(self, image_url: str) -> str:
        """将图片URL转换为Base64数据URI"""
        import base64
        import os
        from django.conf import settings

        try:
            # 如果是HTTP/HTTPS URL，先下载图片
            if image_url.startswith(('http://', 'https://')):
                import requests
                response = requests.get(image_url, timeout=5)  # 优化：减少图片下载超时到5秒
                if response.status_code == 200:
                    image_data = response.content
                    # 检测图片类型
                    content_type = response.headers.get('Content-Type', 'image/jpeg')
                    if not content_type.startswith('image/'):
                        content_type = 'image/jpeg'
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    return f"data:{content_type};base64,{base64_data}"
                else:
                    logger.warning(f"无法下载图片: {image_url}, 状态码: {response.status_code}")
                    return image_url
            else:
                # 本地文件路径
                # 移除开头的 /media/ 或 media/
                relative_path = image_url.lstrip('/')
                if relative_path.startswith('media/'):
                    relative_path = relative_path[6:]  # 移除 'media/'

                file_path = os.path.join(settings.MEDIA_ROOT, relative_path)

                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        image_data = f.read()

                    # 检测图片类型
                    ext = os.path.splitext(file_path)[1].lower()
                    content_type_map = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp'
                    }
                    content_type = content_type_map.get(ext, 'image/jpeg')

                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    return f"data:{content_type};base64,{base64_data}"
                else:
                    logger.warning(f"图片文件不存在: {file_path}")
                    return image_url
        except Exception as e:
            logger.error(f"转换图片为Base64失败: {str(e)}")
            return image_url
            
        else:
            # DashScope原生API格式（非兼容模式）
            # 构建消息历史，DashScope可能需要不同的格式
            messages = self._build_messages(message, history)
            
            # DashScope原生API参数格式
            payload = {
                "model": model,
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "temperature": config.get('temperature', 0.6),
                    "max_tokens": config.get('max_tokens', 2000),
                    "top_p": config.get('top_p', 0.7),
                }
            }
        
        return payload
    
    def _extract_response_content(self, response_data: Dict) -> Dict:
        """从Qwen API响应中提取内容 - 支持多种响应格式"""
        # 首先尝试DashScope原生格式
        if 'output' in response_data and 'text' in response_data['output']:
            # DashScope原生API格式: {"output":{"text":"..."}} 
            content = response_data['output']['text']
            usage_info = response_data.get('usage', {})
        elif 'choices' in response_data and len(response_data['choices']) > 0:
            # OpenAI兼容格式: {"choices":[{"message":{"content":"..."}}]}
            content = response_data['choices'][0]['message']['content']
            usage_info = response_data.get('usage', {})
        else:
            raise Exception("Qwen API响应格式错误: " + str(response_data))
        
        return {
            'content': content,
            'usage': usage_info
        }


class DeepSeekApi(BaseAIApi):
    """DeepSeek API实现 - OpenAI兼容接口"""
    
    def __init__(self):
        super().__init__()
        self.base_url = getattr(settings, 'DEEPSEEK_API_BASE_URL', 'https://api.deepseek.com/v1')
        self.name = "DeepSeek"

    @staticmethod
    def get_supported_models():
        return [
            {'name': 'deepseek-chat', 'label': 'DeepSeek Chat'},
            {'name': 'deepseek-coder', 'label': 'DeepSeek Coder'},
        ]
    
    def _get_api_key(self, model: str) -> Optional[str]:
        return getattr(settings, 'DEEPSEEK_API_KEY', None) or settings.LLM_CONFIG.get('DEEPSEEK_API_KEY')
    
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


class EnhancedApiWrapper:
    """
    增强的API包装器，用于自动处理API密钥缺失的情况
    """
    
    # 存储所有支持的API类
    SUPPORTED_APIS = {
        'qwen': QwenApi,
        'deepseek': DeepSeekApi,
        'openai': OpenAIApi,
        'gemini': GoogleGeminiApi,
        'kimi': MoonshotKimiApi
    }

    @staticmethod
    def get_available_models():
        """
        获取所有可用的AI模型列表
        """
        models = []
        for api_name, api_class in EnhancedApiWrapper.SUPPORTED_APIS.items():
            # 假设每个API类都有一个 `get_supported_models` 方法
            if hasattr(api_class, 'get_supported_models'):
                models.extend(api_class.get_supported_models())
        return models