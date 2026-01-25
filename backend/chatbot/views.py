from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message, PasswordResetToken
from .serializers import ConversationSerializer, MessageSerializer
from django.db.models import Q
import requests
import json
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
import openai

# 导入功能路由模块
from .function_router import FunctionRouter

# 设置OpenAI API密钥
if hasattr(settings, 'LLM_CONFIG'):
    openai.api_key = settings.LLM_CONFIG.get('OPENAI_API_KEY')

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """健康检查接口"""
    return Response({
        'status': 'ok',
        'message': 'AI聊天机器人服务正常运行'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email
        })
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """用户注册"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username': user.username,
        'email': user.email
    }, status=status.HTTP_201_CREATED)

class ConversationViewSet(viewsets.ModelViewSet):
    """会话视图集"""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取用户的会话"""
        return Conversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建会话时设置用户和默认模型"""
        # 从请求中获取模型参数，如果没有则使用默认值
        model = self.request.data.get('model', 'gpt-3.5-turbo')
        serializer.save(user=self.request.user, model=model)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取会话的消息"""
        conversation = self.get_object()
        messages = Message.objects.filter(conversation=conversation)
        serializer = MessageSerializer(messages, many=True)
        
        # 标记未读消息为已读
        messages.filter(role='assistant', is_read=False).update(is_read=True)
        
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    """消息视图集"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取用户的消息"""
        return Message.objects.filter(conversation__user=self.request.user)
    
    def perform_create(self, serializer):
        """创建消息时设置用户"""
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """聊天接口（支持流式响应）"""
        conversation_id = request.data.get('conversation_id')
        message = request.data.get('message')
        image_url = request.data.get('image_url')
        model = request.data.get('model', 'gpt-3.5-turbo')  # 默认模型
        
        try:
            # 创建或获取会话
            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            else:
                # 创建新会话，使用消息前50字符作为标题
                title = message[:50] if len(message) > 50 else message
                conversation = Conversation.objects.create(
                    user=request.user,
                    title=title,
                    model=model  # 保存使用的模型
                )
            
            # 保存用户消息
            user_message = Message.objects.create(
                conversation=conversation,
                role='user',
                content=message,
                image_url=image_url
            )
            
            # 立即返回用户消息和会话信息，然后异步处理AI回复
            response_data = {
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_message).data,
                'ai_message': None,
                'status': 'processing'
            }
            
            # 使用异步任务处理AI回复（这里简化处理，实际项目可使用Celery等）
            try:
                # 调用AI API
                ai_response = self._call_ai_api(conversation, user_message, model)
                
                # 保存AI回复
                ai_message = Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=ai_response
                )
                
                # 更新会话更新时间
                conversation.save()
                
                response_data['ai_message'] = MessageSerializer(ai_message).data
                response_data['status'] = 'completed'
                
            except Exception as e:
                response_data['status'] = 'error'
                response_data['error'] = str(e)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _call_ai_api(self, conversation, user_message, model):
        """调用AI API（优化请求速度）"""
        # 构建对话历史（优化查询和处理）
        history = []
        
        # 获取最近的对话历史（最多8条，减少API调用时间）
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        
        # 只保留用户和助手的消息
        history_messages = []
        for msg in messages:
            if msg.role == 'user':
                if msg.image_url:
                    history_messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": msg.content},
                            {"type": "image_url", "image_url": {"url": msg.image_url}}
                        ]
                    })
                else:
                    history_messages.append({
                        "role": "user",
                        "content": msg.content
                    })
            elif msg.role == 'assistant':
                history_messages.append({
                    "role": "assistant",
                    "content": msg.content
                })
        
        # 最多保留8条对话历史，减少API调用负载
        history = history_messages[-8:]
        
        # 根据模型类型选择API
        if model.startswith('gpt'):
            # OpenAI API
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=history,
                    max_tokens=2000,
                    temperature=0.6,
                    top_p=0.7,
                    top_k=30,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                
                if 'choices' in response and len(response['choices']) > 0:
                    return response['choices'][0]['message']['content']
            except Exception as e:
                return f"抱歉，请求OpenAI服务时发生错误：{str(e)}"
        elif model.startswith('gemini'):
            # Google Gemini API
            api_key = settings.LLM_CONFIG.get('GEMINI_API_KEY')
            if not api_key:
                return "抱歉，Gemini API密钥未配置。"
                
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # 映射模型名称
            if model in ['gemini-pro', 'gemini-1.0-pro']:
                model_name = 'gemini-1.0-pro'
            elif model in ['gemini-1.5-pro']:
                model_name = 'gemini-1.5-pro'
            elif model in ['gemini-ultra', 'gemini-1.0-ultra']:
                model_name = 'gemini-1.0-ultra'
            else:
                model_name = 'gemini-1.0-pro'  # 默认模型

            try:
                gemini_model = genai.GenerativeModel(model_name)
                
                # 将历史消息转换为Gemini格式
                gemini_history = []
                for msg in history:
                    role = 'user' if msg['role'] == 'user' else 'model'  # Gemini使用'model'而不是'assistant'
                    parts = []
                    
                    if isinstance(msg['content'], str):
                        parts.append(msg['content'])
                    elif isinstance(msg['content'], list):
                        for item in msg['content']:
                            if item['type'] == 'text':
                                parts.append(item['text'])
                            elif item['type'] == 'image_url':
                                # Gemini暂时不支持直接处理图像URL，这里简化处理
                                parts.append("用户发送了一张图片")
                    
                    gemini_history.append({
                        'role': role,
                        'parts': parts
                    })
                
                generation_config = {
                    "temperature": 0.6,
                    "top_p": 0.7,
                    "top_k": 30,
                    "max_output_tokens": 2000,
                }
                
                chat = gemini_model.start_chat(history=gemini_history[:-1])  # 除最后一条消息外的所有消息作为历史
                
                # 获取最新消息作为当前请求
                latest_msg = history[-1]
                if isinstance(latest_msg['content'], str):
                    response = chat.send_message(latest_msg['content'], generation_config=generation_config)
                else:
                    # 处理图文消息
                    text_content = ""
                    for item in latest_msg['content']:
                        if item['type'] == 'text':
                            text_content += item['text']
                        elif item['type'] == 'image_url':
                            text_content += " [图片]"
                    response = chat.send_message(text_content, generation_config=generation_config)
                
                if response and hasattr(response, 'text'):
                    return response.text
                else:
                    return "抱歉，我暂时无法回答您的问题。请稍后再试。"
                    
            except Exception as e:
                return f"抱歉，请求Gemini服务时发生错误：{str(e)}"
        elif model.startswith('kimi'):
            # Moonshot Kimi API (假设类似OpenAI接口)
            api_key = settings.LLM_CONFIG.get('KIMI_API_KEY')
            if not api_key:
                return "抱歉，Kimi API密钥未配置。"
                
            url = "https://api.moonshot.cn/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": model,
                "messages": history,
                "max_tokens": 2000,
                "temperature": 0.6,
                "top_p": 0.7,
                "top_k": 30,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                
                return "抱歉，我暂时无法回答您的问题。请稍后再试。"
                
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求Kimi服务时发生错误：{str(e)}"
        elif model.startswith('doubao'):
            # 字节跳动豆包 API
            api_key = settings.LLM_CONFIG.get('DOUBAO_API_KEY')
            if not api_key:
                return "抱歉，豆包API密钥未配置。"
                
            url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": model,
                "messages": history,
                "max_tokens": 2000,
                "temperature": 0.6,
                "top_p": 0.7,
                "top_k": 30,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                
                return "抱歉，我暂时无法回答您的问题。请稍后再试。"
                
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求豆包服务时发生错误：{str(e)}"
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            # 针对代码的Qwen模型
            api_key = settings.LLM_CONFIG.get('QWEN_CODE_API_KEY')
            if not api_key:
                return "抱歉，Qwen_Code API密钥未配置。"
                
            url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": model,
                "messages": history,
                "max_tokens": 2000,
                "temperature": 0.6,
                "top_p": 0.7,
                "top_k": 30,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                
                return "抱歉，我暂时无法回答您的问题。请稍后再试。"
                
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求Qwen_Code服务时发生错误：{str(e)}"
        elif model.startswith('deepseek'):
            # DeepSeek API
            api_key = settings.LLM_CONFIG.get('DEEPSEEK_API_KEY')
            if not api_key:
                return "抱歉，DeepSeek API密钥未配置。"
                
            url = "https://api.deepseek.com/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": model,
                "messages": history,
                "max_tokens": 2000,
                "temperature": 0.6,
                "top_p": 0.7,
                "top_k": 30,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                
                return "抱歉，我暂时无法回答您的问题。请稍后再试。"
                
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求DeepSeek服务时发生错误：{str(e)}"
        elif model.startswith('qwen'):
            # Qwen API
            api_key = settings.LLM_CONFIG.get('QWEN_API_KEY')
            if not api_key:
                return "抱歉，Qwen API密钥未配置。"
                
            url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": model,
                "messages": history,
                "max_tokens": 2000,
                "temperature": 0.6,
                "top_p": 0.7,
                "top_k": 30,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                
                return "抱歉，我暂时无法回答您的问题。请稍后再试。"
                
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求Qwen服务时发生错误：{str(e)}"
        elif model.startswith('zhipu'):
            # 智谱AI API
            api_key = settings.LLM_CONFIG.get('ZHIPU_API_KEY')
            if not api_key:
                return "抱歉，智谱AI API密钥未配置。"
                
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": model,
                "messages": history,
                "max_tokens": 2000,
                "temperature": 0.6,
                "top_p": 0.7,
                "top_k": 30,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                
                return "抱歉，我暂时无法回答您的问题。请稍后再试。"
                
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求智谱AI服务时发生错误：{str(e)}"
        else:
            # 默认使用GPT模型
            try:
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=history,
                    max_tokens=2000,
                    temperature=0.6,
                    top_p=0.7,
                    top_k=30,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                
                if 'choices' in response and len(response['choices']) > 0:
                    return response['choices'][0]['message']['content']
            except Exception as e:
                return f"抱歉，请求AI服务时发生错误：{str(e)}"

@api_view(['GET'])
@permission_classes([AllowAny])
def available_models(request):
    """获取可用的AI模型列表"""
    models = [
        {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'provider': 'OpenAI'},
        {'id': 'gpt-4', 'name': 'GPT-4', 'provider': 'OpenAI'},
        {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'provider': 'OpenAI'},
        {'id': 'gemini-pro', 'name': 'Gemini Pro', 'provider': 'Google'},
        {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'provider': 'Google'},
        {'id': 'kimi-large', 'name': 'Kimi Large', 'provider': 'Moonshot'},
        {'id': 'doubao-pro', 'name': '豆包Pro', 'provider': 'ByteDance'},
        {'id': 'qwen-max', 'name': '通义千问Max', 'provider': 'Alibaba'},
        {'id': 'qwen-plus', 'name': '通义千问Plus', 'provider': 'Alibaba'},
        {'id': 'qwen-turbo', 'name': '通义千问Turbo', 'provider': 'Alibaba'},
        {'id': 'deepseek-chat', 'name': 'DeepSeek Chat', 'provider': 'DeepSeek'},
        {'id': 'zhipu-glm-4', 'name': 'GLM-4', 'provider': 'ZhipuAI'},
        {'id': 'qwen_coder_plus', 'name': '通义千问Coder+', 'provider': 'Alibaba'},
        {'id': 'qwen_code_interpreter', 'name': '通义千问Code Interpreter', 'provider': 'Alibaba'}
    ]
    return Response(models)


# 导入功能路由器
from .function_router import function_router

@api_view(['POST'])
@permission_classes([AllowAny])
def function_router(request):
    """功能路由API - 根据用户输入自动识别意图并调用相应功能"""
    user_input = request.data.get('input', '')
    model = request.data.get('model', 'gpt-3.5-turbo')
    
    if not user_input:
        return Response({'error': '输入内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 初始化功能路由器
        router = FunctionRouter()
        
        # 路由到相应功能
        result = router.route_function(user_input, model)
        
        return Response({
            'success': True,
            'result': result,
            'intent': router.analyze_intent(user_input)
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def function_router_api(request):
    """
    功能路由API端点 - 支持聊天、笑话、故事等多种功能
    """
    try:
        user_input = request.data.get('input', '').strip()
        model = request.data.get('model', 'gpt-3.5-turbo')  # 默认模型
        function_type = request.data.get('function', 'auto')  # 'auto' 表示自动检测功能类型
        
        if not user_input:
            return Response({'error': 'Input is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 使用功能路由系统处理请求
        if function_type == 'auto':
            # 自动检测功能类型
            response_content = function_router.route_function(user_input, model)
        else:
            # 使用指定的功能类型
            handler = getattr(function_router, f"{function_type}_handler", None)
            if handler:
                response_content = handler(user_input, model)
            else:
                response_content = function_router.chat_handler(user_input, model)

        return Response({
            'success': True,
            'response': response_content,
            'function_used': function_router.analyze_intent(user_input) if function_type == 'auto' else function_type
        })

    except Exception as e:
        return Response({'error': f"Function router API error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)















@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """请求密码重置"""
    identifier = request.data.get('identifier')  # 可以是邮箱或用户名
    
    if not identifier:
        return Response({'error': 'Identifier (email or username) is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 首先尝试按邮箱查找用户
    try:
        user = User.objects.get(email=identifier)
    except User.DoesNotExist:
        # 如果邮箱找不到，尝试按用户名查找
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            # 为了安全，即使用户不存在也返回成功消息
            return Response({'message': '如果该账户存在于我们的系统中，您将收到密码重置邮件'})
    
    # 验证用户是否有邮箱（第三方登录用户可能没有邮箱）
    if not user.email:
        return Response({'error': '该账户未绑定邮箱，无法使用密码重置功能'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 删除旧的重置令牌（如果有）
    PasswordResetToken.objects.filter(user=user).delete()
    
    # 生成重置令牌
    import uuid
    from datetime import datetime, timedelta
    
    reset_token = str(uuid.uuid4())
    reset_expiry = datetime.now() + timedelta(hours=1)  # 1小时后过期
    
    # 创建密码重置令牌记录，与用户关联
    PasswordResetToken.objects.create(
        user=user,
        token=reset_token,
        expires_at=reset_expiry
    )
    
    # 构建前端重置链接（用于开发环境调试）
    frontend_base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:5173')
    reset_link = f"{frontend_base_url}/forgot-password?token={reset_token}"
    
    # 模拟发送邮件
    print(f"Password reset token for {user.email} ({user.username}): {reset_token}")
    print(f"Reset link: {reset_link}")
    
    # 在开发环境中返回重置链接，生产环境中会发送邮件
    return Response({
        'message': '如果该账户存在于我们的系统中，您将收到密码重置邮件',
        'reset_link': reset_link,
        'reset_token': reset_token,
        'expires_at': reset_expiry.isoformat()
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """执行密码重置"""
    reset_token = request.data.get('reset_token')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not reset_token or not new_password:
        return Response({'error': 'Reset token and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != confirm_password:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证密码长度不少于6位
    if len(new_password) < 6:
        return Response({'error': 'Password must be at least 6 characters long'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 查找对应的密码重置令牌
        reset_record = PasswordResetToken.objects.select_related('user').get(token=reset_token)
        
        # 检查令牌是否已过期
        if reset_record.is_expired:
            return Response({'error': 'Reset token has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 重置用户密码
        user = reset_record.user
        user.set_password(new_password)
        user.save()
        
        # 删除已使用的重置令牌
        reset_record.delete()
        
        return Response({'message': 'Password has been reset successfully'})
        
    except PasswordResetToken.DoesNotExist:
        return Response({'error': 'Invalid reset token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_test(request):
    """测试环境密码重置 - 直接通过用户名或邮箱重置"""
    identifier = request.data.get('identifier')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not identifier or not new_password:
        return Response({'error': 'Identifier and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != confirm_password:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证密码长度不少于6位
    if len(new_password) < 6:
        return Response({'error': 'Password must be at least 6 characters long'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 首先尝试按邮箱查找用户
    try:
        user = User.objects.get(email=identifier)
    except User.DoesNotExist:
        # 如果邮箱找不到，尝试按用户名查找
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 重置用户密码
    user.set_password(new_password)
    user.save()
    
    return Response({'message': 'Password has been reset successfully'})