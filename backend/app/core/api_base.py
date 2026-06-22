"""
API调用基类，用于封装公共的大模型API调用逻辑
"""
import requests
import json
import logging
import base64
import os
from django.conf import settings
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, unquote
from io import BytesIO

logger = logging.getLogger(__name__)


def _convert_local_image_to_base64(image_url: str) -> Optional[str]:
    """将本地图片URL转换为Base64 Data URI（自动压缩）"""
    try:
        logger.info(f"[B64] 开始: {image_url[:80]}...")
        
        if image_url.startswith('data:image/'):
            return image_url
        
        parsed = urlparse(image_url)
        is_local = parsed.hostname in ('127.0.0.1', 'localhost') or not parsed.hostname or image_url.startswith('/media/')
        
        logger.info(f"[B64] hostname={parsed.hostname}, is_local={is_local}")
        
        if is_local:
            file_path = parsed.path if parsed.path else image_url
            file_path = unquote(file_path)
            
            if file_path.startswith('/media/'):
                file_path = file_path[7:]
            
            media_root = getattr(settings, 'MEDIA_ROOT', '')
            full_path = os.path.join(media_root, file_path.lstrip('/'))
            
            logger.info(f"[B64] 路径={full_path}, 存在={os.path.exists(full_path)}")
            
            if os.path.exists(full_path):
                try:
                    from PIL import Image
                    img = Image.open(full_path)
                    
                    max_size = 512
                    if max(img.size) > max_size:
                        ratio = max_size / max(img.size)
                        img = img.resize((int(img.size[0]*ratio), int(img.size[1]*ratio)), Image.LANCZOS)
                    
                    buf = BytesIO()
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    img.save(buf, format='JPEG', quality=70, optimize=True)
                    data = buf.getvalue()
                    
                    b64 = base64.b64encode(data).decode('utf-8')
                    result = f"data:image/jpeg;base64,{b64}"
                    logger.info(f"[B64] ✅ {len(data)}B -> {len(result)}字符")
                    return result
                    
                except ImportError:
                    with open(full_path, 'rb') as f:
                        data = f.read()
                    ext = os.path.splitext(full_path)[1].lower()
                    mimes = {'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png'}
                    b64 = base64.b64encode(data).decode('utf-8')
                    return f"data:{mimes.get(ext,'image/jpeg')};base64,{b64}"
            else:
                logger.warning(f"[B64] ❌ 文件不存在: {full_path}")
        return image_url
    except Exception as e:
        logger.error(f"[B64] ❌ 失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return image_url

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
    
    def _make_request(self, url: str, headers: Dict, payload: Dict, timeout: int = 120) -> Dict:
        """执行HTTP请求 - 优化：支持大图片和长超时"""
        try:
            import requests.sessions
            # 使用session提高性能
            session = requests.Session()
            session.headers.update({
                'Connection': 'keep-alive',
                'Expect': ''  # 避免100-continue延迟
            })
            
            response = session.post(
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
        
        # 发送请求 - 优化：图片分析需要更长时间
        response_data = self._make_request(
            url=url,
            headers=headers,
            payload=payload,
            timeout=config.get('timeout', 120)  # 默认120秒超时
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
    """通义千问API实现 - 支持OpenAI兼容接口和原生多模态接口"""
    
    def __init__(self):
        super().__init__()
        self.base_url = getattr(settings, 'QWEN_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.name = "Qwen"
        # 百炼原生多模态API端点
        self.multimodal_url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
    
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
        
        # 检查是否是多模态请求（有图片）
        if image_url:
            # 使用百炼原生多模态API（非流式）
            return self._send_multimodal_non_stream(message, config, api_key, image_url)
        else:
            # 使用OpenAI兼容API（纯文本）
            headers = self._prepare_headers(api_key)
            payload = self._prepare_payload(
                message=message,
                history=config.get('history', []),
                config=config
            )
            
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            
            response_data = self._make_request(
                url=url,
                headers=headers,
                payload=payload,
                timeout=config.get('timeout', 15)
            )
            
            return self._extract_response_content(response_data)
    
    def _send_multimodal_non_stream(self, message: str, config: Dict, api_key: str, image_url: str) -> Dict:
        """使用百炼原生多模态API发送非流式请求"""
        model = config.get('model', 'qwen-vl-max')
        
        # 转换图片为Base64
        base64_image = _convert_local_image_to_base64(image_url)
        logger.info(f"非流式多模态请求 - 图片转换完成，长度: {len(base64_image)}")
        
        # 构建消息历史
        messages = []
        
        # 添加系统消息
        messages.append({
            'role': 'system',
            'content': 'You are a helpful assistant.'
        })
        
        # 添加历史消息
        history = config.get('history', [])
        if history:
            for msg in history[-8:]:
                role = msg.get('role', '')
                content = msg.get('content', '')
                
                if role == 'assistant':
                    messages.append({'role': role, 'content': content})
                elif role == 'user':
                    if isinstance(content, list):
                        converted_content = []
                        for item in content:
                            if item.get('type') == 'text':
                                converted_content.append({"text": item['text']})
                            elif item.get('type') == 'image_url' and item.get('image_url', {}).get('url'):
                                original_url = item['image_url']['url']
                                if original_url.startswith('data:image/'):
                                    converted_content.append({"image": original_url})
                                else:
                                    base64_url = _convert_local_image_to_base64(original_url)
                                    if base64_url:
                                        converted_content.append({"image": base64_url})
                        messages.append({'role': role, 'content': converted_content})
                    else:
                        messages.append({'role': role, 'content': content})
                else:
                    messages.append({'role': role, 'content': content})
        
        # 添加当前用户消息（多模态格式）
        content_items = [{"text": message}]
        if base64_image:
            content_items.append({"image": base64_image})
        
        messages.append({
            'role': 'user',
            'content': content_items
        })
        
        # 构建请求载荷（百炼原生格式，非流式）
        payload = {
            "model": model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "incremental_output": False,  # 非流式
                "temperature": config.get('temperature', 0.6),
                "max_tokens": config.get('max_tokens', 2000),
                "top_p": config.get('top_p', 0.7),
            }
        }
        
        # 百炼原生API端点
        url = self.multimodal_url
        
        # 原生API头部
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        logger.info(f"百炼原生多模态API非流式请求 - URL: {url}")
        logger.info(f"百炼原生多模态API非流式请求 - Payload: {json.dumps(payload)[:1000]}")
        
        # 发送请求
        try:
            response = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=(30, 180)
            )
            
            if not response.ok:
                logger.error(f"百炼原生API非流式请求失败: {response.status_code} - {response.text}")
                raise Exception(f"百炼API错误: {response.status_code}")
            
            response_data = response.json()
            logger.info(f"百炼原生API非流式响应: {json.dumps(response_data)[:1000]}")
            
            # 解析响应
            if response_data.get('output') and response_data['output'].get('choices'):
                for choice in response_data['output']['choices']:
                    if choice.get('message') and choice['message'].get('content'):
                        content_list = choice['message']['content']
                        
                        if isinstance(content_list, list):
                            full_content = ""
                            for content_item in content_list:
                                if content_item.get('text'):
                                    full_content += content_item['text']
                            return {'content': full_content, 'usage': {}}
                        elif isinstance(content_list, str):
                            return {'content': content_list, 'usage': {}}
            
            # 格式2: {"output":{"text":"..."}}
            if response_data.get('output') and response_data['output'].get('text'):
                return {'content': response_data['output']['text'], 'usage': {}}
            
            raise Exception("无法解析百炼API响应")
            
        except requests.exceptions.Timeout:
            logger.error("百炼原生API非流式请求超时")
            raise Exception("API请求超时")
        except requests.exceptions.RequestException as e:
            logger.error(f"百炼原生API非流式请求异常: {str(e)}")
            raise Exception(f"API请求异常: {str(e)}")
    
    def send_message_stream(self, message: str, config: Dict):
        """流式发送消息，逐块返回响应"""
        # 验证配置
        self._validate_config(config)
        
        # 获取API密钥
        api_key = self._get_api_key(config.get('model'))
        if not api_key:
            raise Exception(f"未配置{self.name} API密钥")
        
        # 检查是否是多模态消息（包含图片）
        is_multimodal = isinstance(message, list) and any(item.get('type') == 'image_url' for item in message)
        
        if is_multimodal:
            # 使用百炼原生多模态API（支持Base64图片）
            yield from self._send_multimodal_stream(message, config, api_key)
        else:
            # 使用OpenAI兼容API（纯文本）
            yield from self._send_text_stream(message, config, api_key)
    
    def _send_multimodal_stream(self, message: list, config: Dict, api_key: str):
        """使用百炼原生多模态API发送流式请求"""
        model = config.get('model', 'qwen-vl-max')
        
        # ===== 位置 1：确认传入的 message 结构 =====
        logger.info(f"[STREAM DEBUG] message类型: {type(message)}")
        logger.info(f"[STREAM DEBUG] message内容: {json.dumps(message, ensure_ascii=False)[:500]}")
        
        # 处理多模态消息中的本地图片URL - 转换为Base64
        for item in message:
            if item.get('type') == 'image_url' and item.get('image_url', {}).get('url'):
                original_url = item['image_url']['url']
                logger.info(f"开始转换图片URL: {original_url[:100]}")
                base64_url = _convert_local_image_to_base64(original_url)
                item['image_url']['url'] = base64_url
                # ===== 位置 2：确认图片是否转成了 Base64 =====
                logger.info(f"[STREAM DEBUG] 图片转换结果: {base64_url[:80] if base64_url else 'None'}...")
                logger.info(f"[STREAM DEBUG] 是否Base64: {base64_url.startswith('data:image') if base64_url else False}")
                logger.info(f"转换后图片URL长度: {len(base64_url)}, 前50字符: {base64_url[:50]}")
                logger.info(f"多模态消息图片URL处理完成，原长度: {len(original_url)}, 新长度: {len(base64_url)}")
        
        # 构建百炼原生多模态API格式
        # 注意：原生API使用 "image" 字段而不是 "image_url"
        # 注意：原生API的content数组格式是 [{"text": "..."}, {"image": "..."}]
        content_items = []
        for item in message:
            if item.get('type') == 'text':
                content_items.append({"text": item['text']})
            elif item.get('type') == 'image_url':
                # 将 image_url 转换为 image（原生API格式）
                image_url_value = item['image_url']['url']
                logger.info(f"添加到content_items的图片URL长度: {len(image_url_value)}, 前50字符: {image_url_value[:50]}")
                content_items.append({"image": image_url_value})
        
        # 构建消息历史
        messages = []
        
        # 添加系统消息
        messages.append({
            'role': 'system',
            'content': 'You are a helpful assistant. Please format your response in Markdown.'
        })
        
        # 添加历史消息
        history = config.get('history', [])
        if history:
            for msg in history[-8:]:
                role = msg.get('role', '')
                content = msg.get('content', '')
                
                # 百炼原生API：只有user消息可以是数组格式，assistant消息必须是字符串
                if role == 'assistant':
                    # 助手消息保持字符串格式
                    messages.append({'role': role, 'content': content})
                elif role == 'user':
                    # 用户消息如果是多模态则保持数组格式
                    if isinstance(content, list):
                        # 转换历史多模态消息为原生API格式
                        converted_content = []
                        for item in content:
                            if item.get('type') == 'text':
                                converted_content.append({"text": item['text']})
                            elif item.get('type') == 'image_url' and item.get('image_url', {}).get('url'):
                                # 历史消息中的图片也需要转换为Base64
                                original_url = item['image_url']['url']
                                if original_url.startswith('data:image/'):
                                    # 已经是Base64，直接使用
                                    converted_content.append({"image": original_url})
                                else:
                                    # 需要转换为Base64
                                    base64_url = _convert_local_image_to_base64(original_url)
                                    if base64_url:
                                        converted_content.append({"image": base64_url})
                                    else:
                                        logger.warning(f"历史消息图片转换失败: {original_url[:100]}")
                        messages.append({'role': role, 'content': converted_content})
                    else:
                        messages.append({'role': role, 'content': content})
                else:
                    messages.append({'role': role, 'content': content})
        
        # 添加当前用户消息（多模态格式）
        messages.append({
            'role': 'user',
            'content': content_items
        })
        
        # 构建请求载荷（百炼原生格式）
        payload = {
            "model": model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "incremental_output": True,  # 启用增量输出（流式）
                "temperature": config.get('temperature', 0.6),
                "max_tokens": config.get('max_tokens', 2000),
                "top_p": config.get('top_p', 0.7),
            }
        }
        
        # ===== 位置 3：确认发给百炼的 payload 格式 =====
        logger.info(f"[STREAM DEBUG] payload: {json.dumps(payload, ensure_ascii=False)[:800]}")
        
        # 百炼原生API端点
        url = self.multimodal_url
        
        # 原生API使用不同的头部格式
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'X-DashScope-SSE': 'enable'  # 启用SSE
        }
        
        logger.info(f"百炼原生多模态API请求 - URL: {url}")
        logger.info(f"百炼原生多模态API请求 - Payload: {json.dumps(payload)[:1000]}")
        
        # 发送流式请求
        try:
            session = requests.Session()
            session.headers.update({
                'Connection': 'keep-alive',
                'Expect': ''
            })
            
            response = session.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=(30, 180),
                stream=True
            )
            
            if not response.ok:
                # ===== 位置 4：确认百炼返回的状态码和第一行数据 =====
                logger.error(f"[STREAM DEBUG] 百炼状态码: {response.status_code}")
                logger.error(f"[STREAM DEBUG] 百炼响应头: {dict(response.headers)}")
                logger.error(f"[STREAM DEBUG] 百炼错误响应体: {response.text[:500]}")
                logger.error(f"{self.name} 多模态API请求失败: {response.status_code} - {response.text}")
                raise Exception(f"{self.name} API错误: {response.status_code}")
            
            logger.info(f"百炼原生多模态API响应状态码: {response.status_code}")
            logger.info(f"[STREAM DEBUG] 百炼状态码: {response.status_code}")
            logger.info(f"[STREAM DEBUG] 百炼响应头: {dict(response.headers)}")
            
            # 逐块读取SSE响应 - 修复版：增强容错和日志
            line_count = 0
            yield_count = 0
            
            try:
                for line in response.iter_lines():
                    line_count += 1
                    if not line:
                        continue
                        
                    line_str = line.decode('utf-8')
                    logger.info(f"[RAW SSE #{line_count}] {line_str[:300]}")
                    
                    # 跳过SSE注释行（:HTTP_STATUS/200 或 :ok）
                    if line_str.startswith(':'):
                        continue
                    
                    # 跳过 event/id 行
                    if line_str.startswith('event:') or line_str.startswith('id:'):
                        continue
                    
                    # 处理 data: 行（兼容 data: 和 data:  两种格式）
                    if line_str.startswith('data:'):
                        data_str = line_str[5:].strip()  # 去掉 "data:" 前缀并去除前后空格
                        
                        # 结束标记
                        if data_str == '[DONE]':
                            logger.info("[SSE] 收到 [DONE]，流结束")
                            break
                        
                        # 跳过空 data
                        if not data_str:
                            continue
                        
                        # 尝试解析JSON
                        try:
                            data = json.loads(data_str)
                            logger.info(f"[PARSED] JSON结构: {list(data.keys())}")
                            
                            # 检查是否有错误字段
                            if 'code' in data and 'message' in data:
                                logger.error(f"[API ERROR] 百炼返回错误: {data}")
                                raise Exception(f"百炼API错误: {data.get('message', '未知错误')}")
                            
                            # 格式1: {"output": {"choices": [{"message": {"content": [{"text":"..."}]}}]}}
                            if data.get('output') and data['output'].get('choices'):
                                for choice in data['output']['choices']:
                                    finish_reason = choice.get('finish_reason', '')
                                    logger.info(f"[CHOICE] finish_reason={finish_reason}")
                                    
                                    if choice.get('message') and choice['message'].get('content'):
                                        content_list = choice['message']['content']
                                        
                                        if isinstance(content_list, list):
                                            for content_item in content_list:
                                                if content_item.get('text'):
                                                    text_content = content_item['text']
                                                    logger.info(f"[YIELD] 内容: {text_content[:50]}")
                                                    yield text_content
                                                    yield_count += 1
                                        elif isinstance(content_list, str):
                                            if content_list:
                                                logger.info(f"[YIELD] 字符串内容: {content_list[:50]}")
                                                yield content_list
                                                yield_count += 1
                            # 格式2: {"output":{"text":"..."}}
                            elif data.get('output') and data['output'].get('text'):
                                content = data['output']['text']
                                if content:
                                    logger.info(f"[YIELD] output.text: {content[:50]}")
                                    yield content
                                    yield_count += 1
                            else:
                                logger.warning(f"[UNKNOWN] 未识别的响应格式: {json.dumps(data)[:200]}")
                                
                        except json.JSONDecodeError as e:
                            logger.warning(f"[JSON ERROR] 解析失败: {str(e)}")
                            logger.warning(f"[JSON ERROR] 原始数据: {data_str[:300]}")
                            continue
                        except Exception as e:
                            logger.error(f"[PARSE ERROR] 解析异常: {str(e)}")
                            import traceback
                            logger.error(f"[PARSE ERROR] 详细错误: {traceback.format_exc()}")
                            continue
            except Exception as e:
                logger.error(f"SSE流读取异常: {str(e)}")
                import traceback
                logger.error(f"详细错误: {traceback.format_exc()}")
                raise
            finally:
                logger.info(f"SSE流处理完成 - 读取{line_count}行，yield{yield_count}次")
            
        except requests.exceptions.Timeout:
            logger.error(f"{self.name} 多模态API请求超时")
            raise Exception(f"{self.name} API请求超时")
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.name} 多模态API请求异常: {str(e)}")
            raise Exception(f"{self.name} API请求异常: {str(e)}")
    
    def _send_text_stream(self, message: str, config: Dict, api_key: str):
        """使用OpenAI兼容API发送纯文本流式请求"""
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
            # 使用session提高性能
            session = requests.Session()
            session.headers.update({
                'Connection': 'keep-alive',
                'Expect': ''
            })
            
            response = session.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=(30, 180),  # 连接超时30秒，读取超时180秒（图片分析需要更长时间）
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
            
            # 非视觉模型但包含图片时，也需要转换本地图片为Base64
            elif any(isinstance(msg.get('content'), list) for msg in payload.get('messages', [])):
                for msg in payload.get('messages', []):
                    if isinstance(msg.get('content'), list):
                        for item in msg['content']:
                            if item.get('type') == 'image_url':
                                image_url = item.get('image_url', {}).get('url', '')
                                if image_url and image_url.startswith(('http://', 'https://')):
                                    # 检查是否是本地地址
                                    if '127.0.0.1' in image_url or 'localhost' in image_url:
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