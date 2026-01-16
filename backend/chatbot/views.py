from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
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
                
                # 将对话历史转换为Gemini格式
                gemini_history = []
                for msg in history:
                    role = 'user' if msg['role'] == 'user' else 'model'
                    content = msg['content']
                    if isinstance(content, list):
                        # 处理图文混合内容
                        parts = []
                        for item in content:
                            if item['type'] == 'text':
                                parts.append(item['text'])
                            elif item['type'] == 'image_url':
                                # 注意：Gemini需要直接的图像数据，这里只是示意
                                # 实际应用中需要下载图像并转换为适当格式
                                parts.append(f"[图像: {item['image_url']['url']}]")
                        gemini_history.append({'role': role, 'parts': parts})
                    else:
                        gemini_history.append({'role': role, 'parts': [content]})
                
                # 生成内容
                chat = gemini_model.start_chat(history=gemini_history)
                response = chat.send_message(msg.content)
                
                return response.text
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
        else:
            # 默认使用CSDN AI API
            url = "https://models.csdn.net/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-oxpetfthyrbxzgxyonrmssftsbgbfhpxuhtvoihmqhotm"
            }
            
            # 选择模型
            selected_model = "qwen-vl-plus" if user_message.image_url else "Deepseek-V3"
            
            data = {
                "model": selected_model,
                "stream": False,
                "messages": history,
                "max_tokens": 2000,  # 减少回复长度，提升响应速度
                "temperature": 0.6,  # 稍微降低随机性，提升回复速度
                "top_p": 0.7,
                "top_k": 30,  # 减少候选token数量，提升响应速度
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            try:
                # 优化超时时间
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                
                return "抱歉，我暂时无法回答您的问题。请稍后再试。"
                
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求AI服务时发生错误：{str(e)}"

@api_view(['GET'])
@permission_classes([AllowAny])
def available_models(request):
    """返回可用的大模型列表"""
    models = [
        {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'provider': 'OpenAI'},
        {'id': 'gpt-4', 'name': 'GPT-4', 'provider': 'OpenAI'},
        {'id': 'gemini-pro', 'name': 'Gemini Pro', 'provider': 'Google'},
        {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'provider': 'Google'},
        {'id': 'kimi-large', 'name': 'Kimi Large', 'provider': 'Moonshot AI'},
        {'id': 'doubao-pro', 'name': '豆包Pro', 'provider': 'ByteDance'},
        {'id': 'qwen-code', 'name': 'Qwen-Code', 'provider': 'Alibaba Cloud'},
        {'id': 'qwen-code-coder', 'name': 'Qwen-Code-Coder', 'provider': 'Alibaba Cloud'},
        {'id': 'deepseek-chat', 'name': 'DeepSeek Chat', 'provider': 'DeepSeek'},
        {'id': 'deepseek-coder', 'name': 'DeepSeek Coder', 'provider': 'DeepSeek'},
        {'id': 'qwen-max', 'name': 'Qwen Max', 'provider': 'Alibaba Cloud'},
        {'id': 'qwen-plus', 'name': 'Qwen Plus', 'provider': 'Alibaba Cloud'},
        {'id': 'qwen-turbo', 'name': 'Qwen Turbo', 'provider': 'Alibaba Cloud'}
    ]
    return Response(models)


# 微信OAuth登录相关功能
@api_view(['GET'])
@permission_classes([AllowAny])
def wechat_auth_url(request):
    """获取微信授权URL"""
    # 微信开放平台配置
    app_id = settings.WECHAT_CONFIG.get('APP_ID', 'your_wechat_app_id')
    redirect_uri = settings.WECHAT_CONFIG.get('REDIRECT_URI', 'http://127.0.0.1:8000/api/v1/auth/wechat/callback/')
    
    # 生成state参数用于防止CSRF攻击
    import secrets
    state = secrets.token_urlsafe(16)
    request.session['wechat_state'] = state
    
    # 构建微信授权URL
    auth_url = (
        f"https://open.weixin.qq.com/connect/qrconnect?"
        f"appid={app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=snsapi_login&"
        f"state={state}#wechat_redirect"
    )
    
    return Response({'auth_url': auth_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def wechat_auth_callback(request):
    """微信授权回调处理"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    # 验证state参数
    if not code or not state or state != request.session.get('wechat_state'):
        return Response({'error': '无效的授权请求'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 清除session中的state
    request.session.pop('wechat_state', None)
    
    try:
        # 通过code获取access_token
        app_id = settings.WECHAT_CONFIG.get('APP_ID')
        app_secret = settings.WECHAT_CONFIG.get('APP_SECRET')
        
        token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?"
        token_params = {
            'appid': app_id,
            'secret': app_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.get(token_url, params=token_params, timeout=10)
        token_data = token_response.json()
        
        if 'errcode' in token_data:
            return Response({'error': f"微信授权失败: {token_data.get('errmsg', '未知错误')}"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_data['access_token']
        openid = token_data['openid']
        
        # 获取用户信息
        user_info_url = f"https://api.weixin.qq.com/sns/userinfo?"
        user_info_params = {
            'access_token': access_token,
            'openid': openid
        }
        
        user_info_response = requests.get(user_info_url, params=user_info_params, timeout=10)
        user_info = user_info_response.json()
        
        if 'errcode' in user_info:
            return Response({'error': f"获取用户信息失败: {user_info.get('errmsg', '未知错误')}"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # 创建或获取用户
        username = f"wechat_{openid}"
        nickname = user_info.get('nickname', '微信用户')
        avatar = user_info.get('headimgurl', '')
        
        # 查找是否已有微信用户
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 创建新用户
            user = User.objects.create_user(
                username=username,
                email=f"{username}@wechat.com",
                password=secrets.token_urlsafe(32)  # 随机密码
            )
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'nickname': nickname,
            'avatar': avatar,
            'provider': 'wechat'
        })
        
    except Exception as e:
        return Response({'error': f"微信登录处理失败: {str(e)}"}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# QQ OAuth登录相关功能
@api_view(['GET'])
@permission_classes([AllowAny])
def qq_auth_url(request):
    """获取QQ授权URL"""
    app_id = settings.QQ_CONFIG.get('APP_ID', 'your_qq_app_id')
    redirect_uri = settings.QQ_CONFIG.get('REDIRECT_URI', 'http://127.0.0.1:8000/api/v1/auth/qq/callback/')
    
    # 生成state参数用于防止CSRF攻击
    import secrets
    state = secrets.token_urlsafe(16)
    request.session['qq_state'] = state
    
    # 构建QQ授权URL
    auth_url = (
        f"https://graph.qq.com/oauth2.0/authorize?"
        f"response_type=code&"
        f"client_id={app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"state={state}&"
        f"scope=get_user_info"
    )
    
    return Response({'auth_url': auth_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def qq_auth_callback(request):
    """QQ授权回调处理"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    # 验证state参数
    if not code or not state or state != request.session.get('qq_state'):
        return Response({'error': '无效的授权请求'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 清除session中的state
    request.session.pop('qq_state', None)
    
    try:
        app_id = settings.QQ_CONFIG.get('APP_ID')
        app_key = settings.QQ_CONFIG.get('APP_KEY')
        redirect_uri = settings.QQ_CONFIG.get('REDIRECT_URI')
        
        # 通过code获取access_token
        token_url = "https://graph.qq.com/oauth2.0/token"
        token_params = {
            'grant_type': 'authorization_code',
            'client_id': app_id,
            'client_secret': app_key,
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        token_response = requests.get(token_url, params=token_params, timeout=10)
        token_text = token_response.text
        
        # 解析access_token (QQ返回的是text格式: access_token=YOUR_ACCESS_TOKEN&expires_in=7776000)
        if 'access_token' not in token_text:
            return Response({'error': '获取access_token失败'}, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_text.split('access_token=')[1].split('&')[0]
        
        # 获取openid
        openid_url = "https://graph.qq.com/oauth2.0/me"
        openid_params = {'access_token': access_token}
        
        openid_response = requests.get(openid_url, params=openid_params, timeout=10)
        openid_text = openid_response.text
        
        # 解析openid (返回格式: callback( {"client_id":"YOUR_APP_ID","openid":"YOUR_OPENID"} ))
        import json
        openid_data = json.loads(openid_text.replace('callback(', '').replace(');', ''))
        openid = openid_data.get('openid')
        
        if not openid:
            return Response({'error': '获取openid失败'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户信息
        user_info_url = "https://graph.qq.com/user/get_user_info"
        user_info_params = {
            'access_token': access_token,
            'oauth_consumer_key': app_id,
            'openid': openid
        }
        
        user_info_response = requests.get(user_info_url, params=user_info_params, timeout=10)
        user_info = user_info_response.json()
        
        if user_info.get('ret') != 0:
            return Response({'error': f"获取用户信息失败: {user_info.get('msg', '未知错误')}"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # 创建或获取用户
        username = f"qq_{openid}"
        nickname = user_info.get('nickname', 'QQ用户')
        avatar = user_info.get('figureurl_qq_2', user_info.get('figureurl_qq_1', ''))
        
        # 查找是否已有QQ用户
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 创建新用户
            user = User.objects.create_user(
                username=username,
                email=f"{username}@qq.com",
                password=secrets.token_urlsafe(32)  # 随机密码
            )
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'nickname': nickname,
            'avatar': avatar,
            'provider': 'qq'
        })
        
    except Exception as e:
        return Response({'error': f"QQ登录处理失败: {str(e)}"}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# GitHub OAuth登录相关功能
@api_view(['GET'])
@permission_classes([AllowAny])
def github_auth_url(request):
    """获取GitHub授权URL"""
    client_id = settings.GITHUB_CONFIG.get('CLIENT_ID', 'your_github_client_id')
    redirect_uri = settings.GITHUB_CONFIG.get('REDIRECT_URI', 'http://127.0.0.1:8000/api/v1/auth/github/callback/')
    
    # 生成state参数用于防止CSRF攻击
    import secrets
    state = secrets.token_urlsafe(16)
    request.session['github_state'] = state
    
    # 构建GitHub授权URL
    auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"state={state}&"
        f"scope=user:email"
    )
    
    return Response({'auth_url': auth_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def github_auth_callback(request):
    """GitHub授权回调处理"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    # 验证state参数
    if not code or not state or state != request.session.get('github_state'):
        return Response({'error': '无效的授权请求'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 清除session中的state
    request.session.pop('github_state', None)
    
    try:
        client_id = settings.GITHUB_CONFIG.get('CLIENT_ID')
        client_secret = settings.GITHUB_CONFIG.get('CLIENT_SECRET')
        redirect_uri = settings.GITHUB_CONFIG.get('REDIRECT_URI')
        
        # 通过code获取access_token
        token_url = "https://github.com/login/oauth/access_token"
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_data, headers={'Accept': 'application/json'}, timeout=10)
        token_data = token_response.json()
        
        if 'error' in token_data:
            return Response({'error': f"获取access_token失败: {token_data.get('error_description', '未知错误')}"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_data.get('access_token')
        
        if not access_token:
            return Response({'error': '获取access_token失败'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户信息
        user_info_url = "https://api.github.com/user"
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/json'
        }
        
        user_info_response = requests.get(user_info_url, headers=headers, timeout=10)
        user_info = user_info_response.json()
        
        if 'message' in user_info and user_info['message'] == 'Bad credentials':
            return Response({'error': 'GitHub认证失败'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户邮箱（GitHub邮箱可能为私有）
        email_url = "https://api.github.com/user/emails"
        email_response = requests.get(email_url, headers=headers, timeout=10)
        emails = email_response.json()
        
        primary_email = None
        for email in emails:
            if email.get('primary') and email.get('verified'):
                primary_email = email.get('email')
                break
        
        # 创建或获取用户
        username = f"github_{user_info.get('id')}"
        nickname = user_info.get('name', user_info.get('login', 'GitHub用户'))
        avatar = user_info.get('avatar_url', '')
        email = primary_email or f"{username}@github.com"
        
        # 查找是否已有GitHub用户
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 创建新用户
            user = User.objects.create_user(
                username=username,
                email=email,
                password=secrets.token_urlsafe(32)  # 随机密码
            )
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'nickname': nickname,
            'avatar': avatar,
            'provider': 'github'
        })
        
    except Exception as e:
        return Response({'error': f"GitHub登录处理失败: {str(e)}"}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)