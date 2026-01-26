from django.shortcuts import render
from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from .models import Conversation, Message, PasswordResetToken
from .serializers import ConversationSerializer, MessageSerializer, PasswordResetTokenSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
import json
import requests
import openai
import logging
from .function_router import FunctionRouter
from .middleware.rate_limit import rate_limit

logger = logging.getLogger(__name__)

# 导入功能路由器
from .function_router import FunctionRouter
function_router = FunctionRouter()


class ConversationViewSet(viewsets.ModelViewSet):
    """会话视图集"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')
    
    def perform_create(self, serializer):
        """确保创建会话时用户已认证"""
        # 确保用户已认证
        if not self.request.user.is_authenticated:
            raise exceptions.PermissionDenied("用户未认证")
        # 保存时指定当前用户
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取会话的消息"""
        try:
            conversation = self.get_object()
            # 额外检查会话是否属于当前用户
            if conversation.user != request.user:
                return Response({
                    'error': '无权访问此会话'
                }, status=status.HTTP_403_FORBIDDEN)
            
            messages = Message.objects.filter(conversation=conversation).order_by('created_at')
            serializer = MessageSerializer(messages, many=True)
            
            # 标记未读消息为已读
            messages.filter(role='assistant', is_read=False).update(is_read=True)
            
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response({
                'error': '会话不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"获取消息列表失败: {str(e)}")
            return Response({
                'error': '获取消息列表失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MessageViewSet(viewsets.ModelViewSet):
    """消息视图集"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Message.objects.filter(conversation__user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """确保创建消息时验证会话归属和用户权限"""
        # 确保用户已认证
        if not self.request.user.is_authenticated:
            raise exceptions.PermissionDenied("用户未认证")
        
        # 获取请求中的会话ID
        conversation_id = self.request.data.get('conversation_id')
        if not conversation_id:
            raise exceptions.ValidationError("必须提供会话ID")
        
        # 验证会话属于当前用户
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=self.request.user)
        except Conversation.DoesNotExist:
            raise exceptions.PermissionDenied("会话不存在或不属于当前用户")
        
        # 保存消息，确保与正确的会话关联
        serializer.save(conversation=conversation)
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """聊天接口（支持流式响应）"""
        conversation_id = request.data.get('conversation_id')
        message = request.data.get('message')
        image_url = request.data.get('image_url')
        model = request.data.get('model', 'gpt-3.5-turbo')  # 默认模型
        
        try:
            # 验证用户是否已认证
            if not request.user.is_authenticated:
                return Response({
                    'error': '用户未认证，请先登录'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
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
            api_key = getattr(request.user, 'profile', None) and request.user.profile.gemini_api_key
            if not api_key:
                # 如果用户没有配置，尝试使用全局配置
                api_key = settings.LLM_CONFIG.get('GEMINI_API_KEY')
            if not api_key:
                return "抱歉，Google Gemini API密钥未配置。"
                
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

                # 开始聊天
                chat = gemini_model.start_chat(history=gemini_history[:-1])  # 除了最后一条消息外的所有历史
                
                # 发送最后一条消息
                response = chat.send_message(
                    gemini_history[-1]['parts'],  # 最后一条消息的内容
                    generation_config=generation_config
                )
                
                return response.text
                
            except Exception as e:
                return f"抱歉，请求Google Gemini服务时发生错误：{str(e)}"
        elif model.startswith('kimi'):  # Moonshot Kimi API
            api_key = getattr(request.user, 'profile', None) and request.user.profile.kimi_api_key
            if not api_key:
                # 如果用户没有配置，尝试使用全局配置
                api_key = settings.LLM_CONFIG.get('KIMI_API_KEY')
            if not api_key:
                return "抱歉，Kimi API密钥未配置。"
                
            try:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                url = settings.LLM_CONFIG.get('KIMI_API_BASE_URL', 'https://api.moonshot.cn/v1/chat/completions')
                
                data = {
                    'model': model,
                    'messages': history,
                    'max_tokens': 2000,
                    'temperature': 0.6,
                    'top_p': 0.7,
                    'top_k': 30,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                }
                
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        return response_data['choices'][0]['message']['content']
                    else:
                        return "抱歉，Kimi API响应格式错误。"
                else:
                    return f"抱歉，请求Kimi服务时发生错误：{response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求Kimi服务时发生错误：{str(e)}"
        elif model.startswith('doubao'):  # 字节跳动豆包API
            api_key = getattr(request.user, 'profile', None) and request.user.profile.doubao_api_key
            if not api_key:
                # 如果用户没有配置，尝试使用全局配置
                api_key = settings.LLM_CONFIG.get('DOUBAO_API_KEY')
            if not api_key:
                return "抱歉，豆包API密钥未配置。"
                
            try:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                # 豆包API的URL和具体参数可能需要根据实际文档调整
                url = settings.LLM_CONFIG.get('DOUBAO_API_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions')
                
                data = {
                    'model': model,
                    'messages': history,
                    'max_tokens': 2000,
                    'temperature': 0.6,
                    'top_p': 0.7,
                    'top_k': 30,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                }
                
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        return response_data['choices'][0]['message']['content']
                    else:
                        return "抱歉，豆包API响应格式错误。"
                else:
                    return f"抱歉，请求豆包服务时发生错误：{response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求豆包服务时发生错误：{str(e)}"
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            # 针对代码的Qwen模型
            api_key = getattr(request.user, 'profile', None) and request.user.profile.qwen_code_api_key
            if not api_key:
                # 如果用户没有配置，尝试使用全局配置
                api_key = settings.LLM_CONFIG.get('QWEN_CODE_API_KEY')
            if not api_key:
                return "抱歉，通义千问代码API密钥未配置。"
                
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
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        return response_data['choices'][0]['message']['content']
                    else:
                        return "抱歉，Qwen_Code API响应格式错误。"
                else:
                    return f"抱歉，请求Qwen_Code服务时发生错误：{response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求Qwen_Code服务时发生错误：{str(e)}"
        elif model.startswith('deepseek'):
            # DeepSeek API - 优先使用用户的API密钥
            api_key = getattr(request.user, 'profile', None) and request.user.profile.deepseek_api_key
            if not api_key:
                # 如果用户没有配置，尝试使用全局配置
                api_key = settings.LLM_CONFIG.get('DEEPSEEK_API_KEY')
            if not api_key:
                return "抱歉，DeepSeek API密钥未配置。"
                
            url = "https://api.deepseek.com/v1/chat/completions"
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
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        return response_data['choices'][0]['message']['content']
                    else:
                        return "抱歉，DeepSeek API响应格式错误。"
                else:
                    return f"抱歉，请求DeepSeek服务时发生错误：{response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求DeepSeek服务时发生错误：{str(e)}"
        elif model.startswith('qwen'):
            # Qwen API
            api_key = getattr(request.user, 'profile', None) and request.user.profile.qwen_api_key
            if not api_key:
                # 如果用户没有配置，尝试使用全局配置
                api_key = settings.LLM_CONFIG.get('QWEN_API_KEY')
            if not api_key:
                return "抱歉，通义千问API密钥未配置。"
                
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
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        return response_data['choices'][0]['message']['content']
                    else:
                        return "抱歉，Qwen API响应格式错误。"
                else:
                    return f"抱歉，请求Qwen服务时发生错误：{response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                return "抱歉，请求超时。请稍后再试。"
            except requests.exceptions.RequestException as e:
                return f"抱歉，请求Qwen服务时发生错误：{str(e)}"
        else:
            # 默认使用OpenAI API
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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@rate_limit(max_requests=30, window_size=60, block_malicious=True)  # 每分钟最多30次聊天请求
def chat(request):
    """聊天接口（非流式响应）"""
    # 输入验证
    conversation_id = request.data.get('conversation_id')
    message = request.data.get('message')
    image_url = request.data.get('image_url')
    model = request.data.get('model', 'gpt-3.5-turbo')
    
    # 验证输入数据
    is_valid, validated_message = validate_input_data(message, '消息', max_length=5000)
    if not is_valid:
        return Response({'error': validated_message}, status=status.HTTP_400_BAD_REQUEST)
    
    if image_url:
        is_valid, validated_image_url = validate_input_data(image_url, '图片URL', max_length=2000)
        if not is_valid:
            return Response({'error': validated_image_url}, status=status.HTTP_400_BAD_REQUEST)
    
    if model:
        is_valid, validated_model = validate_input_data(model, '模型', max_length=100)
        if not is_valid:
            return Response({'error': validated_model}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 创建或获取会话
        if conversation_id:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        else:
            title = validated_message[:50] if len(validated_message) > 50 else validated_message
            conversation = Conversation.objects.create(
                user=request.user,
                title=title,
                model=validated_model
            )
        
        # 保存用户消息
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=validated_message,
            image_url=validated_image_url if image_url else None
        )
        
        # 调用AI API
        history = []
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        for msg in messages:
            if msg.role == 'user':
                if msg.image_url:
                    history.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": msg.content},
                            {"type": "image_url", "image_url": {"url": msg.image_url}}
                        ]
                    })
                else:
                    history.append({
                        "role": "user",
                        "content": msg.content
                    })
            elif msg.role == 'assistant':
                history.append({
                    "role": "assistant",
                    "content": msg.content
                })
        
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
                    response_text = response['choices'][0]['message']['content']
                else:
                    response_text = "抱歉，AI服务暂时不可用。"
            except Exception as e:
                response_text = f"抱歉，请求OpenAI服务时发生错误：{str(e)}"
        else:
            # 使用通用API调用函数
            response_text = _call_ai_api_sync(conversation, user_message, model)
        
        # 保存AI回复
        ai_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=response_text
        )
        
        return Response({
            'conversation_id': conversation.id,
            'user_message': MessageSerializer(user_message).data,
            'ai_message': MessageSerializer(ai_message).data,
            'model_used': model
        })
        
    except Conversation.DoesNotExist:
        return Response({'error': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Chat API error: {str(e)}")
        return Response({'error': '聊天服务暂时不可用'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@rate_limit(max_requests=30, window_size=60, block_malicious=True)  # 每分钟最多30次流式聊天请求
def stream_chat(request):
    """流式聊天接口"""
    # 输入验证
    conversation_id = request.data.get('conversation_id')
    message = request.data.get('message')
    image_url = request.data.get('image_url')
    model = request.data.get('model', 'gpt-3.5-turbo')
    
    # 验证输入数据
    is_valid, validated_message = validate_input_data(message, '消息', max_length=5000)
    if not is_valid:
        return Response({'error': validated_message}, status=status.HTTP_400_BAD_REQUEST)
    
    if image_url:
        is_valid, validated_image_url = validate_input_data(image_url, '图片URL', max_length=2000)
        if not is_valid:
            return Response({'error': validated_image_url}, status=status.HTTP_400_BAD_REQUEST)
    
    if model:
        is_valid, validated_model = validate_input_data(model, '模型', max_length=100)
        if not is_valid:
            return Response({'error': validated_model}, status=status.HTTP_400_BAD_REQUEST)
    
    def event_stream():
        try:
            # 创建或获取会话
            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            else:
                title = validated_message[:50] if len(validated_message) > 50 else validated_message
                conversation = Conversation.objects.create(
                    user=request.user,
                    title=title,
                    model=validated_model
                )
            
            # 保存用户消息
            user_message = Message.objects.create(
                conversation=conversation,
                role='user',
                content=validated_message,
                image_url=validated_image_url if image_url else None
            )
            
            # 发送初始消息
            yield f"data: {json.dumps({'type': 'user_message', 'message': MessageSerializer(user_message).data})}\n\n"
            
            # 根据模型类型选择流式API
            if model.startswith('gpt'):
                # OpenAI流式API
                try:
                    response = openai.ChatCompletion.create(
                        model=model,
                        messages=[{"role": m['role'], "content": m['content']} for m in _build_history(conversation)],
                        max_tokens=2000,
                        temperature=0.6,
                        top_p=0.7,
                        top_k=30,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                        stream=True  # 启用流式响应
                    )
                    
                    full_response = ""
                    for chunk in response:
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0]['delta']
                            if 'content' in delta:
                                content = delta['content']
                                full_response += content
                                
                                # 发送流式数据
                                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                    
                    # 保存完整的AI回复
                    ai_message = Message.objects.create(
                        conversation=conversation,
                        role='assistant',
                        content=full_response
                    )
                    
                    # 发送完成信号
                    yield f"data: {json.dumps({'type': 'complete', 'message': MessageSerializer(ai_message).data})}\n\n"
                    
                except Exception as e:
                    error_msg = f"抱歉，请求OpenAI服务时发生错误：{str(e)}"
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
            
            else:
                # 对于其他模型，我们模拟流式响应
                try:
                    # 调用非流式API获取完整响应
                    full_response = _call_ai_api_sync(conversation, user_message, model)
                    
                    # 模拟流式发送（逐字发送）
                    words = full_response.split(' ')
                    full_response_text = ""
                    
                    for word in words:
                        full_response_text += word + " "
                        yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                    
                    # 保存完整的AI回复
                    ai_message = Message.objects.create(
                        conversation=conversation,
                        role='assistant',
                        content=full_response
                    )
                    
                    # 发送完成信号
                    yield f"data: {json.dumps({'type': 'complete', 'message': MessageSerializer(ai_message).data})}\n\n"
                    
                except Exception as e:
                    error_msg = f"抱歉，请求AI服务时发生错误：{str(e)}"
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                    
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def validate_input_data(data, field_name, max_length=1000, allow_empty=False):
    """
    验证输入数据的安全性和有效性
    
    Args:
        data: 待验证的数据
        field_name: 字段名
        max_length: 最大长度限制
        allow_empty: 是否允许空值
    
    Returns:
        tuple: (is_valid, validated_data or error_message)
    """
    if not data:
        if allow_empty:
            return True, data
        return False, f"{field_name} 不能为空"
    
    # 类型检查
    if not isinstance(data, str):
        return False, f"{field_name} 必须是字符串类型"
    
    # 长度检查
    if len(data) > max_length:
        return False, f"{field_name} 长度不能超过 {max_length} 个字符"
    
    # 检测潜在的恶意内容
    dangerous_patterns = [
        '<script', 'javascript:', 'vbscript:', 'onerror=', 'onload=',
        'alert(', 'eval(', 'document.cookie', 'window.location'
    ]
    
    cleaned_data = data.lower().strip()
    for pattern in dangerous_patterns:
        if pattern in cleaned_data:
            return False, f"{field_name} 包含不安全的内容"
    
    return True, data.strip()


def _build_history(conversation):
    """构建对话历史"""
    messages = Message.objects.filter(conversation=conversation).order_by('created_at')
    history = []
    for msg in messages:
        if msg.role == 'user':
            history.append({"role": "user", "content": msg.content})
        elif msg.role == 'assistant':
            history.append({"role": "assistant", "content": msg.content})
    return history


def _call_ai_api_sync(conversation, user_message, model):
    """同步调用AI API（复用现有逻辑）"""
    # 构建对话历史
    history = []
    
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
    
    # 最多保留8条对话历史
    history = history_messages[-8:]
    
    # 根据模型类型选择API（与原逻辑相同）
    if model.startswith('gpt'):
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
        api_key = getattr(request.user, 'profile', None) and request.user.profile.gemini_api_key
        if not api_key:
            # 如果用户没有配置，尝试使用全局配置
            api_key = settings.LLM_CONFIG.get('GEMINI_API_KEY')
        if not api_key:
            return "抱歉，Gemini API密钥未配置。"
            
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        if model in ['gemini-pro', 'gemini-1.0-pro']:
            model_name = 'gemini-1.0-pro'
        elif model in ['gemini-1.5-pro']:
            model_name = 'gemini-1.5-pro'
        elif model in ['gemini-ultra', 'gemini-1.0-ultra']:
            model_name = 'gemini-1.0-ultra'
        else:
            model_name = 'gemini-1.0-pro'

        try:
            gemini_model = genai.GenerativeModel(model_name)
            
            gemini_history = []
            for msg in history:
                role = 'user' if msg['role'] == 'user' else 'model'
                parts = []
                
                if isinstance(msg['content'], str):
                    parts.append(msg['content'])
                elif isinstance(msg['content'], list):
                    for item in msg['content']:
                        if item['type'] == 'text':
                            parts.append(item['text'])
                        elif item['type'] == 'image_url':
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

            chat = gemini_model.start_chat(history=gemini_history[:-1])
            response = chat.send_message(
                gemini_history[-1]['parts'],
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            return f"抱歉，请求Google Gemini服务时发生错误：{str(e)}"
    elif model.startswith('kimi'):
        api_key = getattr(request.user, 'profile', None) and request.user.profile.kimi_api_key
        if not api_key:
            # 如果用户没有配置，尝试使用全局配置
            api_key = settings.LLM_CONFIG.get('KIMI_API_KEY')
        if not api_key:
            return "抱歉，Kimi API密钥未配置。"
            
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            url = settings.LLM_CONFIG.get('KIMI_API_BASE_URL', 'https://api.moonshot.cn/v1/chat/completions')
            
            data = {
                'model': model,
                'messages': history,
                'max_tokens': 2000,
                'temperature': 0.6,
                'top_p': 0.7,
                'top_k': 30,
                'frequency_penalty': 0.0,
                'presence_penalty': 0.0
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data['choices'][0]['message']['content']
                else:
                    return "抱歉，Kimi API响应格式错误。"
            else:
                return f"抱歉，请求Kimi服务时发生错误：{response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "抱歉，请求超时。请稍后再试。"
        except requests.exceptions.RequestException as e:
            return f"抱歉，请求Kimi服务时发生错误：{str(e)}"
    elif model.startswith('doubao'):
        api_key = getattr(request.user, 'profile', None) and request.user.profile.doubao_api_key
        if not api_key:
            # 如果用户没有配置，尝试使用全局配置
            api_key = settings.LLM_CONFIG.get('DOUBAO_API_KEY')
        if not api_key:
            return "抱歉，豆包API密钥未配置。"
            
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            url = settings.LLM_CONFIG.get('DOUBAO_API_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions')
            
            data = {
                'model': model,
                'messages': history,
                'max_tokens': 2000,
                'temperature': 0.6,
                'top_p': 0.7,
                'top_k': 30,
                'frequency_penalty': 0.0,
                'presence_penalty': 0.0
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data['choices'][0]['message']['content']
                else:
                    return "抱歉，豆包API响应格式错误。"
            else:
                return f"抱歉，请求豆包服务时发生错误：{response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "抱歉，请求超时。请稍后再试。"
        except requests.exceptions.RequestException as e:
            return f"抱歉，请求豆包服务时发生错误：{str(e)}"
    elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
        # Qwen Code API - 优先使用用户的API密钥
        api_key = getattr(request.user, 'profile', None) and request.user.profile.qwen_code_api_key
        if not api_key:
            # 如果用户没有配置，尝试使用全局配置
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
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data['choices'][0]['message']['content']
                else:
                    return "抱歉，Qwen_Code API响应格式错误。"
            else:
                return f"抱歉，请求Qwen_Code服务时发生错误：{response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "抱歉，请求超时。请稍后再试。"
        except requests.exceptions.RequestException as e:
            return f"抱歉，请求Qwen_Code服务时发生错误：{str(e)}"
    elif model.startswith('deepseek'):
        # DeepSeek API - 优先使用用户的API密钥
        api_key = getattr(request.user, 'profile', None) and request.user.profile.deepseek_api_key
        if not api_key:
            # 如果用户没有配置，尝试使用全局配置
            api_key = settings.LLM_CONFIG.get('DEEPSEEK_API_KEY')
        if not api_key:
            return "抱歉，DeepSeek API密钥未配置。"
            
        url = "https://api.deepseek.com/v1/chat/completions"
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
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data['choices'][0]['message']['content']
                else:
                    return "抱歉，DeepSeek API响应格式错误。"
            else:
                return f"抱歉，请求DeepSeek服务时发生错误：{response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "抱歉，请求超时。请稍后再试。"
        except requests.exceptions.RequestException as e:
            return f"抱歉，请求DeepSeek服务时发生错误：{str(e)}"
    elif model.startswith('qwen'):
        # Qwen API - 优先使用用户的API密钥
        api_key = getattr(request.user, 'profile', None) and request.user.profile.qwen_api_key
        if not api_key:
            # 如果用户没有配置，尝试使用全局配置
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
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data['choices'][0]['message']['content']
                else:
                    return "抱歉，Qwen API响应格式错误。"
            else:
                return f"抱歉，请求Qwen服务时发生错误：{response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "抱歉，请求超时。请稍后再试。"
        except requests.exceptions.RequestException as e:
            return f"抱歉，请求Qwen服务时发生错误：{str(e)}"
    else:
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
@permission_classes([permissions.AllowAny])
def available_models(request):
    """获取可用模型列表"""
    # 从请求中获取用户信息
    user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
    
    # 初始化用户API密钥配置
    user_api_keys = {}
    if user and hasattr(user, 'profile'):
        profile = user.profile
        user_api_keys = {
            'openai': profile.openai_api_key if profile.openai_api_key else settings.LLM_CONFIG.get('OPENAI_API_KEY'),
            'deepseek': profile.deepseek_api_key if profile.deepseek_api_key else settings.LLM_CONFIG.get('DEEPSEEK_API_KEY'),
            'qwen': profile.qwen_api_key if profile.qwen_api_key else settings.LLM_CONFIG.get('QWEN_API_KEY'),
            'gemini': profile.gemini_api_key if profile.gemini_api_key else settings.LLM_CONFIG.get('GEMINI_API_KEY'),
            'kimi': profile.kimi_api_key if profile.kimi_api_key else settings.LLM_CONFIG.get('KIMI_API_KEY'),
            'doubao': profile.doubao_api_key if profile.doubao_api_key else settings.LLM_CONFIG.get('DOUBAO_API_KEY'),
            'qwen_code': profile.qwen_code_api_key if profile.qwen_code_api_key else settings.LLM_CONFIG.get('QWEN_CODE_API_KEY'),
        }
    else:
        # 如果用户未登录或无配置，则使用全局配置
        user_api_keys = {
            'openai': settings.LLM_CONFIG.get('OPENAI_API_KEY'),
            'deepseek': settings.LLM_CONFIG.get('DEEPSEEK_API_KEY'),
            'qwen': settings.LLM_CONFIG.get('QWEN_API_KEY'),
            'gemini': settings.LLM_CONFIG.get('GEMINI_API_KEY'),
            'kimi': settings.LLM_CONFIG.get('KIMI_API_KEY'),
            'doubao': settings.LLM_CONFIG.get('DOUBAO_API_KEY'),
            'qwen_code': settings.LLM_CONFIG.get('QWEN_CODE_API_KEY'),
        }
    
    # 根据用户配置的API密钥决定哪些模型可用
    available_models_list = []
    
    # OpenAI 模型
    if user_api_keys.get('openai'):
        available_models_list.extend([
            {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'provider': 'OpenAI', 'available': True},
            {'id': 'gpt-4', 'name': 'GPT-4', 'provider': 'OpenAI', 'available': True},
            {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'provider': 'OpenAI', 'available': True},
            {'id': 'gpt-4o', 'name': 'GPT-4o', 'provider': 'OpenAI', 'available': True},
            {'id': 'gpt-4o-mini', 'name': 'GPT-4o Mini', 'provider': 'OpenAI', 'available': True},
        ])
    
    # Google Gemini 模型
    if user_api_keys.get('gemini'):
        available_models_list.extend([
            {'id': 'gemini-pro', 'name': 'Gemini Pro', 'provider': 'Google', 'available': True},
            {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'provider': 'Google', 'available': True},
            {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash', 'provider': 'Google', 'available': True},
        ])
    
    # 阿里通义千问系列
    if user_api_keys.get('qwen') or user_api_keys.get('qwen_code'):
        available_models_list.extend([
            {'id': 'qwen-max', 'name': '通义千问Max', 'provider': 'Alibaba', 'available': True},
            {'id': 'qwen-plus', 'name': '通义千问Plus', 'provider': 'Alibaba', 'available': True},
            {'id': 'qwen-turbo', 'name': '通义千问Turbo', 'provider': 'Alibaba', 'available': True},
            {'id': 'qwen-coder', 'name': '通义千问Coder', 'provider': 'Alibaba', 'available': True},
            {'id': 'qwen-math', 'name': '通义千问Math', 'provider': 'Alibaba', 'available': True},
            {'id': 'qwen-vl-max', 'name': '通义千问VL-Max', 'provider': 'Alibaba', 'available': True},  # 视觉语言模型
            {'id': 'qwen-vl-plus', 'name': '通义千问VL-Plus', 'provider': 'Alibaba', 'available': True},  # 视觉语言模型
            {'id': 'qwen-audio-turbo', 'name': '通义千问Audio-Turbo', 'provider': 'Alibaba', 'available': True},  # 音频模型
            {'id': 'qwen_coder_plus', 'name': '通义千问Coder+', 'provider': 'Alibaba', 'available': True},
            {'id': 'qwen_code_interpreter', 'name': '通义千问Code Interpreter', 'provider': 'Alibaba', 'available': True}
        ])
    
    # DeepSeek
    if user_api_keys.get('deepseek'):
        available_models_list.extend([
            {'id': 'deepseek-chat', 'name': 'DeepSeek Chat', 'provider': 'DeepSeek', 'available': True},
            {'id': 'deepseek-coder', 'name': 'DeepSeek Coder', 'provider': 'DeepSeek', 'available': True},
        ])
    
    # 月之暗面(Kimi)
    if user_api_keys.get('kimi'):
        available_models_list.extend([
            {'id': 'kimi-large', 'name': 'Kimi Large', 'provider': 'Moonshot', 'available': True},
        ])
    
    # 豆包
    if user_api_keys.get('doubao'):
        available_models_list.extend([
            {'id': 'doubao-pro', 'name': '豆包Pro', 'provider': 'ByteDance', 'available': True},
        ])
    
    # 其他模型（如果全局配置中有API密钥）
    if settings.LLM_CONFIG.get('ANTHROPIC_API_KEY'):
        available_models_list.extend([
            {'id': 'claude-3-haiku', 'name': 'Claude 3 Haiku', 'provider': 'Anthropic', 'available': True},
            {'id': 'claude-3-sonnet', 'name': 'Claude 3 Sonnet', 'provider': 'Anthropic', 'available': True},
            {'id': 'claude-3-opus', 'name': 'Claude 3 Opus', 'provider': 'Anthropic', 'available': True},
            {'id': 'claude-3-5-sonnet', 'name': 'Claude 3.5 Sonnet', 'provider': 'Anthropic', 'available': True},
        ])
    
    if settings.LLM_CONFIG.get('BAIDU_API_KEY'):
        available_models_list.extend([
            {'id': 'ernie-bot-4.5', 'name': '文心一言4.5', 'provider': 'Baidu', 'available': True},
            {'id': 'ernie-bot-4', 'name': '文心一言4', 'provider': 'Baidu', 'available': True},
        ])
    
    if settings.LLM_CONFIG.get('IFLYTEK_API_KEY'):
        available_models_list.extend([
            {'id': 'spark-max', 'name': '讯飞星火Max', 'provider': 'iFlytek', 'available': True},
            {'id': 'spark-pro', 'name': '讯飞星火Pro', 'provider': 'iFlytek', 'available': True},
            {'id': 'spark-lite', 'name': '讯飞星火Lite', 'provider': 'iFlytek', 'available': True},
        ])
    
    if settings.LLM_CONFIG.get('ZHIPU_API_KEY'):
        available_models_list.extend([
            {'id': 'glm-4', 'name': 'GLM-4', 'provider': 'ZhipuAI', 'available': True},
            {'id': 'glm-4-air', 'name': 'GLM-4 Air', 'provider': 'ZhipuAI', 'available': True},
            {'id': 'glm-4-flash', 'name': 'GLM-4 Flash', 'provider': 'ZhipuAI', 'available': True},
        ])
    
    return Response(available_models_list)


# 导入功能路由器
from .function_router import function_router

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@rate_limit(max_requests=20, window_size=60, block_malicious=True)  # 每分钟最多20次功能路由请求
def function_router(request):
    """功能路由API - 根据用户输入自动识别意图并调用相应功能"""
    user_input = request.data.get('input', '')
    model = request.data.get('model', 'gpt-3.5-turbo')
    
    # 验证输入数据
    is_valid, validated_input = validate_input_data(user_input, '输入', max_length=2000)
    if not is_valid:
        return Response({'error': validated_input}, status=status.HTTP_400_BAD_REQUEST)
    
    if model:
        is_valid, validated_model = validate_input_data(model, '模型', max_length=100)
        if not is_valid:
            return Response({'error': validated_model}, status=status.HTTP_400_BAD_REQUEST)
    
    if not validated_input:
        return Response({'error': '输入内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 初始化功能路由器
        router = FunctionRouter()
        result = router.route_function(validated_input, validated_model)
        return Response({'result': result})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@rate_limit(max_requests=10, window_size=300, block_malicious=False)  # 5分钟内最多10次登录尝试，开发环境减少误判
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            from rest_framework_simplejwt.tokens import RefreshToken
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username,
                'email': user.email,
            })
        else:
            return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@rate_limit(max_requests=3, window_size=3600, block_malicious=True)  # 1小时内最多3次注册
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({'error': '邮箱已被注册'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        validate_password(password)
    except ValidationError as e:
        return Response({'error': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username': user.username,
        'email': user.email,
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'AI聊天机器人服务正常运行'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@rate_limit(max_requests=3, window_size=300, block_malicious=True)  # 5分钟内最多3次密码重置请求
def request_password_reset(request):
    """请求密码重置"""
    email_or_username = request.data.get('email_or_username')
    
    if not email_or_username:
        return Response({'error': '邮箱或用户名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 首先尝试按邮箱查找用户
        try:
            user = User.objects.get(email=email_or_username)
        except User.DoesNotExist:
            # 如果邮箱找不到，尝试按用户名查找
            user = User.objects.get(username=email_or_username)
        
        # 删除旧的重置令牌
        PasswordResetToken.objects.filter(user=user).delete()
        
        # 生成重置令牌
        reset_token = str(uuid.uuid4())
        reset_expiry = timezone.now() + timedelta(hours=1)  # 1小时后过期
        
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
    except User.DoesNotExist:
        # 为了安全考虑，不暴露用户是否存在
        return Response({
            'message': '如果该账户存在于我们的系统中，您将收到密码重置邮件'
        })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@rate_limit(max_requests=5, window_size=300, block_malicious=True)  # 5分钟内最多5次密码重置尝试
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
@permission_classes([permissions.AllowAny])
@rate_limit(max_requests=10, window_size=60, block_malicious=True)  # 每分钟最多10次测试重置请求
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