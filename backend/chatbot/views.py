from django.shortcuts import render
from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from .models import Conversation, Message, PasswordResetToken, UserProfile
from .serializers import ConversationSerializer, MessageSerializer, PasswordResetTokenSerializer, UserSerializer, UserProfileSerializer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.cache import cache
import uuid
import json
import requests
import openai
import logging
import hashlib
import socket
from PIL import Image
import os
from .enhanced_api import EnhancedApiWrapper
from .function_router import FunctionRouter
from .middleware.rate_limit import rate_limit

logger = logging.getLogger(__name__)

# 导入功能路由器
from .function_router import FunctionRouter
from .utils.knowledge_base import real_time_source
function_router_instance = FunctionRouter()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """健康检查"""
    return Response({"status": "ok"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chat(request):
    """非流式聊天接口"""
    conversation_id = request.data.get('conversation_id')
    message_content = request.data.get('message')
    image_url = request.data.get('image_url')
    model = request.data.get('model', 'qwen-turbo')

    logger.info(f"chat 被调用 - message: {message_content[:50]}..., model: {model}")
    
    # 优化：添加缓存键定义
    cache_key = f"chat_cache_{hashlib.md5(message_content.encode()).hexdigest()}"
    
    # 优化：尝试从缓存获取响应
    try:
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"✅ 使用缓存响应，节省 API 调用")
            return Response({
                'content': cached_response,
                'conversation_id': conversation_id,
                'status': 'completed',
                'from_cache': True
            })
    except Exception as cache_error:
        logger.warning(f"缓存不可用，跳过缓存：{cache_error}")

    try:
        if conversation_id:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        else:
            title = message_content[:50] if message_content else "New Conversation"
            conversation = Conversation.objects.create(user=request.user, title=title, model=model)

        # 保存用户消息
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=message_content,
            image_url=image_url
        )

        # 构建历史
        history = []
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        for msg in messages:
            if msg.role == 'user':
                content = [{"type": "text", "text": msg.content}]
                if msg.image_url:
                    content.append({"type": "image_url", "image_url": {"url": msg.image_url}})
                history.append({"role": "user", "content": content if len(content) > 1 else content[0]['text']})
            elif msg.role == 'assistant':
                history.append({"role": "assistant", "content": msg.content})

        # 优化：在发送消息前，先检查知识库（带超时限制）
        knowledge_context = ""
        try:
            # 优化：设置 1.5 秒超时，避免知识库检索拖慢响应
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(1.5)

            from .utils.knowledge_base import knowledge_base_manager
            if knowledge_base_manager.client is not None:
                # 优化：减少检索数量从 2 到 1，加快检索速度
                search_results = knowledge_base_manager.search(message_content, n_results=1)
                if search_results and search_results.get('documents'):
                    kb_docs = search_results['documents'][0]
                    if kb_docs:
                        # 只使用最相关的 1 条，减少上下文长度
                        knowledge_context = "\n".join(kb_docs[:1]) + "\n\n"

            socket.setdefaulttimeout(old_timeout)
        except Exception as kb_error:
            logger.warning(f"⚠️ 知识库检索超时或失败（已跳过）: {str(kb_error)}")
            # 知识库检索失败不影响主要功能，继续执行

        # 准备发送给 AI 的消息，包含知识库上下文
        enhanced_message = knowledge_context + message_content if knowledge_context else message_content
        
        # 创建API实例
        api_instance = EnhancedApiWrapper.create_api_instance(model)

        try:
            result = api_instance.send_message(
                message=enhanced_message,
                config={
                    'model': model,
                    'history': history[:-1] if history else [],
                    'temperature': 0.7,
                    'max_tokens': 2000,
                    'top_p': 0.9
                },
                image_url=image_url
            )
            content = result['content']
        except Exception as api_error:
            logger.warning(f"API调用失败，使用模拟响应: {str(api_error)}")
            from .enhanced_api import MockApiInstance
            mock_api = MockApiInstance()
            result = mock_api.send_message(
                message=message_content,
                config={'model': model}
            )
            content = result['content']

        # 保存AI回复
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=content
        )
        conversation.save()
        
        # 优化：缓存响应
        try:
            cache.set(cache_key, content, 3600)  # 缓存 1 小时
            logger.info(f"✅ 已缓存响应到缓存系统")
        except Exception as cache_error:
            logger.warning(f"缓存保存失败：{cache_error}")

        return Response({
            'content': content,
            'conversation_id': conversation.id,
            'status': 'completed'
        })

    except Conversation.DoesNotExist:
        return Response({'error': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def stream_chat(request):
    """流式聊天接口"""
    try:
        conversation_id = request.data.get('conversation_id')
        message_content = request.data.get('message')
        image_url = request.data.get('image_url')
        model = request.data.get('model', 'gpt-3.5-turbo')
        role_id = request.data.get('role_id')
        custom_role_prompt = request.data.get('custom_role_prompt')

        # 调试日志
        logger.info(f"stream_chat 被调用 - user: {request.user}, message: {message_content[:50] if message_content else 'None'}, image_url: {image_url}, model: {model}, role_id: {role_id}")

        # 如果上传了图片但当前模型不支持视觉，自动切换到视觉模型
        vision_models = ['qwen-vl-plus', 'qwen-vl-max', 'gpt-4-vision', 'gpt-4o', 'claude-3-opus', 'claude-3-sonnet']
        if image_url and model not in vision_models:
            # 尝试使用 qwen-vl-plus 作为默认视觉模型
            original_model = model
            model = 'qwen-vl-plus'
            logger.info(f"检测到图片但模型 {original_model} 不支持视觉，自动切换到 {model}")

        if conversation_id:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        else:
            title = (message_content or "New Conversation")[:50]
            conversation = Conversation.objects.create(user=request.user, title=title, model=model)

        message_data = {
            'conversation': conversation,
            'role': 'user',
            'content': message_content,
        }
        if image_url:
            message_data['image_url'] = image_url
        Message.objects.create(**message_data)

        history = []
        
        # 如果指定了角色，添加系统提示词
        if role_id:
            role_info = function_router_instance.role_presets.get(role_id, {})
            system_prompt = role_info.get('system_prompt', '')
            
            # 如果是自定义角色，使用用户提供的提示词
            if role_id == 'custom' and custom_role_prompt:
                system_prompt = custom_role_prompt
            
            if system_prompt:
                history.append({"role": "system", "content": system_prompt})
                logger.info(f"添加角色系统提示词: {role_info.get('name', '自定义角色')}")
        
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        for msg in messages:
            if msg.role == 'user':
                content = [{"type": "text", "text": msg.content}]
                if msg.image_url:
                    content.append({"type": "image_url", "image_url": {"url": msg.image_url}})
                history.append({"role": "user", "content": content if len(content) > 1 else content[0]['text']})
            elif msg.role == 'assistant':
                history.append({"role": "assistant", "content": msg.content})

        # 添加缓存键定义（用于缓存响应）
        # 修复：缓存键必须包含图片URL，否则相同文字不同图片会命中错误缓存
        cache_key_data = (message_content or '') + (image_url or '')
        cache_key = f"chat_cache_{hashlib.md5(cache_key_data.encode()).hexdigest()}"
        
        # 创建API实例
        logger.info(f"创建API实例，模型: {model}")
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        logger.info(f"API实例创建成功: {api_instance.name}")

        def stream_response_generator():
            full_response = ""
            try:
                # 优化：首先检查缓存
                try:
                    cached_response = cache.get(cache_key)
                    if cached_response:
                        logger.info(f"✅ 使用缓存响应，节省 API 调用")
                        yield f"data: {json.dumps({'content': ' '})}" + "\n\n"
                        yield f"data: {json.dumps({'content': cached_response})}" + "\n\n"
                        yield f"data: {json.dumps({'status': 'completed', 'from_cache': True})}" + "\n\n"
                        return
                except Exception as cache_error:
                    logger.warning(f"缓存检查失败：{cache_error}")
                
                # 优化：立即返回一个空格，让前端更快显示响应开始
                yield f"data: {json.dumps({'content': ' '})}" + "\n\n"
                
                # 优化：移除知识库检索，直接发送消息给 AI，最大化响应速度
                knowledge_context = ""
                safe_message = message_content or ""
                enhanced_message = safe_message
                
                # 使用api_instance发送消息
                # 如果有图片，构建包含图片的消息内容
                current_message_content = enhanced_message
                logger.info(f"准备发送消息 - image_url: {image_url}, message_type: {type(current_message_content)}")
                if image_url:
                    # 构建多模态消息内容
                    current_message_content = [
                        {"type": "text", "text": enhanced_message},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                    logger.info(f"构建多模态消息内容: {current_message_content}")

                try:
                    # 检查API实例是否支持流式输出
                    if hasattr(api_instance, 'send_message_stream'):
                        # 使用真正的流式输出
                        stream_count = 0
                        logger.info(f"开始流式输出 - message类型: {type(current_message_content)}")
                        try:
                            for content_chunk in api_instance.send_message_stream(
                                message=current_message_content,
                                config={
                                    'model': model,
                                    'history': history[:-1] if len(history) > 1 else [],
                                    'temperature': 0.7,
                                    'max_tokens': 2000,
                                    'top_p': 0.9
                                }
                            ):
                                stream_count += 1
                                full_response += content_chunk
                                logger.info(f"流式响应 #{stream_count}: {content_chunk[:50]}")
                                # 逐块返回内容
                                yield f"data: {json.dumps({'content': content_chunk})}" + "\n\n"
                            logger.info(f"流式响应完成 - 共{stream_count}块，总长度: {len(full_response)}")
                        except Exception as stream_error:
                            logger.error(f"流式输出异常: {str(stream_error)}")
                            import traceback
                            logger.error(f"流式输出详细错误: {traceback.format_exc()}")
                            raise
                    else:
                        # 回退到非流式方式
                        result = api_instance.send_message(
                            message=current_message_content,
                            config={
                                'model': model,
                                'history': history[:-1] if len(history) > 1 else [],
                                'temperature': 0.7,
                                'max_tokens': 2000,
                                'top_p': 0.9
                            }
                        )
                        content = result['content']
                        full_response = content
                        # 一次性返回内容
                        yield f"data: {json.dumps({'content': content})}" + "\n\n"
                except Exception as api_error:
                    # API调用失败，使用模拟响应
                    logger.warning(f"API调用失败，使用模拟响应: {str(api_error)}")
                    import traceback
                    logger.error(f"API错误详情: {traceback.format_exc()}")
                    from .enhanced_api import MockApiInstance
                    mock_api = MockApiInstance()
                    result = mock_api.send_message(
                        message=current_message_content,
                        config={'model': model}
                    )
                    content = result['content']
                    full_response = content
                    # 一次性返回内容
                    yield f"data: {json.dumps({'content': content})}" + "\n\n"

                if full_response:
                    # 优化：缓存响应，下次相同请求直接返回
                    try:
                        cache.set(cache_key, full_response, 3600)  # 缓存 1 小时
                        logger.info(f"✅ 已缓存响应到缓存系统")
                    except Exception as cache_error:
                        logger.warning(f"缓存设置失败: {cache_error}")
                    
                    Message.objects.create(
                        conversation=conversation,
                        role='assistant',
                        content=full_response
                    )
                    conversation.save() # Update updated_at
                    yield f"data: {json.dumps({'status': 'completed', 'conversation_id': conversation.id})}" + "\n\n"
                else:
                    yield f"data: {json.dumps({'error': 'Empty response from AI'})}" + "\n\n"

            except Exception as e:
                import traceback
                logger.error(f"Streaming chat error: {str(e)}")
                logger.error(f"详细错误: {traceback.format_exc()}")
                yield f"data: {json.dumps({'error': str(e)})}" + "\n\n"

        response = StreamingHttpResponse(stream_response_generator(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # 禁用 Nginx 缓冲
        return response

    except Conversation.DoesNotExist:
        return Response({'error': '会话不存在或不属于当前用户'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Stream chat setup error: {str(e)}")
        logger.error(f"详细错误信息: {error_traceback}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def function_router(request):
    # 兼容新旧两种参数格式
    feature_name = request.data.get('feature_name') or request.data.get('function')
    user_input = request.data.get('user_input') or request.data.get('input')
    language = request.data.get('language')
    model = request.data.get('model', 'qwen-turbo')
    image_url = request.data.get('image_url')
    role_id = request.data.get('role_id')
    custom_role_prompt = request.data.get('custom_role_prompt')

    if not feature_name or not user_input:
        return Response({'error': 'Feature name and user input are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 将 feature_name 作为用户输入的一部分传入 route_function
        full_input = f"{feature_name} {user_input}".strip()
        response_content = function_router_instance.route_function(full_input, model=model, language=language, image_url=image_url, role_id=role_id, custom_role_prompt=custom_role_prompt)
        return Response({'result': response_content})
    except Exception as e:
        logger.error(f"Error in function router: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
def stream_function_router_view(request):
    """流式功能路由器视图"""
    try:
        data = json.loads(request.body)
        feature_name = data.get('feature_name') or data.get('function')
        user_input = data.get('user_input') or data.get('input')
        language = data.get('language')
        model = data.get('model', 'qwen-turbo')
        image_url = data.get('image_url')
        role_id = data.get('role_id')
        custom_role_prompt = data.get('custom_role_prompt')

        if not feature_name or not user_input:
            return JsonResponse({'error': 'Feature name and user input are required.'}, status=400)

        return stream_function_router(feature_name, user_input, model, language, image_url, role_id, custom_role_prompt)
    except Exception as e:
        logger.error(f"Error in stream_function_router_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def stream_function_router(feature_name, user_input, model, language, image_url, role_id, custom_role_prompt):
    """流式功能路由器"""
    logger.info(f"开始流式处理 - feature: {feature_name}, model: {model}, role_id: {role_id}")
    
    def generate():
        try:
            full_input = f"{feature_name} {user_input}".strip()
            logger.info(f"完整输入: {full_input[:100]}")
            
            # 如果指定了角色，优先使用角色扮演功能
            if role_id and role_id != 'none':
                logger.info(f"使用角色扮演模式，角色: {role_id}")
                result = stream_role_play(user_input, model, role_id, custom_role_prompt, image_url)
            else:
                # 分析意图并路由到相应功能
                intent = function_router_instance.analyze_intent(full_input)
                logger.info(f"识别意图: {intent}")
                
                if intent == 'unknown':
                    result = stream_chat_handler(full_input, model, image_url)
                elif intent == 'translation':
                    result = stream_generic_handler(full_input, model, 'translation_handler', language, image_url)
                elif intent == 'programming':
                    result = stream_generic_handler(full_input, model, 'programming_handler', image_url=image_url)
                elif intent == 'story':
                    result = stream_generic_handler(full_input, model, 'story_handler', image_url=image_url)
                elif intent == 'poetry':
                    result = stream_generic_handler(full_input, model, 'poetry_handler', image_url=image_url)
                elif intent == 'chengyu':
                    result = stream_generic_handler(full_input, model, 'chengyu_handler', image_url=image_url)
                elif intent == 'text_summary':
                    result = stream_generic_handler(full_input, model, 'text_summary_handler', image_url=image_url)
                elif intent == 'report_generator':
                    result = stream_generic_handler(full_input, model, 'report_generator_handler', image_url=image_url)
                elif intent == 'travel_planner':
                    result = stream_generic_handler(full_input, model, 'travel_planner_handler', image_url=image_url)
                elif intent == 'social_media_copywriter':
                    result = stream_generic_handler(full_input, model, 'social_media_copywriter_handler', image_url=image_url)
                elif intent == 'visual_idiom_puzzle':
                    result = stream_generic_handler(full_input, model, 'visual_idiom_puzzle_handler', image_url=image_url)
                else:
                    handler = function_router_instance.functions.get(intent, function_router_instance.chat_handler)
                    import inspect
                    sig = inspect.signature(handler)
                    if 'image_url' in sig.parameters:
                        result = handler(full_input, model, image_url)
                    else:
                        result = handler(full_input, model)
                    yield f"data: {json.dumps({'content': result})}" + "\n\n"
                    yield f"data: {json.dumps({'status': 'completed'})}" + "\n\n"
                    return
            
            # 流式输出
            logger.info("开始流式输出")
            for chunk in result:
                yield f"data: {json.dumps({'content': chunk})}" + "\n\n"
            
            yield f"data: {json.dumps({'status': 'completed'})}" + "\n\n"
            logger.info("流式输出完成")
            
        except Exception as e:
            logger.error(f"Error in stream function router: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}" + "\n\n"
            yield f"data: {json.dumps({'status': 'completed'})}" + "\n\n"

    response = StreamingHttpResponse(generate(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def stream_generic_handler(user_input, model, handler_name, language=None, image_url=None):
    """通用流式处理器，用于编程、故事等功能"""
    from .enhanced_api import EnhancedApiWrapper
    
    api_instance = EnhancedApiWrapper.create_api_instance(model)
    
    if hasattr(api_instance, 'send_message_stream'):
        config = {
            'model': model,
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.9,
            'history': [{"role": "user", "content": user_input}]
        }
        
        for chunk in api_instance.send_message_stream(user_input, config):
            yield chunk
    else:
        handler = getattr(function_router_instance, handler_name, None)
        if handler:
            import inspect
            sig = inspect.signature(handler)
            if 'language' in sig.parameters and language:
                result = handler(user_input, model, language)
            elif 'image_url' in sig.parameters and image_url:
                result = handler(user_input, model, image_url)
            else:
                result = handler(user_input, model)
            yield result


def stream_chat_handler(user_input, model, image_url=None):
    """流式聊天处理器"""
    from .enhanced_api import EnhancedApiWrapper
    
    api_instance = EnhancedApiWrapper.create_api_instance(model)
    
    if hasattr(api_instance, 'send_message_stream'):
        config = {
            'model': model,
            'temperature': 0.6,
            'max_tokens': 2000,
            'top_p': 0.7,
            'history': [{"role": "user", "content": user_input}]
        }
        
        current_message_content = user_input
        if image_url:
            current_message_content = [
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        
        for chunk in api_instance.send_message_stream(current_message_content, config):
            yield chunk
    else:
        result = api_instance.send_message(user_input, {'model': model}, image_url=image_url)
        yield result.get('content', '')


def stream_role_play(user_input, model, role_id, custom_role_prompt=None, image_url=None):
    """流式角色扮演处理器"""
    from .enhanced_api import EnhancedApiWrapper
    
    role_info = function_router_instance.role_presets.get(role_id, function_router_instance.role_presets['custom'])
    system_prompt = role_info['system_prompt']
    
    if role_id == 'custom' and custom_role_prompt:
        system_prompt = custom_role_prompt
    
    history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    api_instance = EnhancedApiWrapper.create_api_instance(model)
    
    if hasattr(api_instance, 'send_message_stream'):
        config = {
            'model': model,
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.8,
            'history': history
        }
        
        current_message_content = user_input
        if image_url:
            current_message_content = [
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        
        for chunk in api_instance.send_message_stream(current_message_content, config):
            yield chunk
    else:
        config = {
            'model': model,
            'temperature': 0.7,
            'max_tokens': 800,
            'history': history
        }
        result = api_instance.send_message(user_input, config, image_url=image_url)
        yield result.get('content', '')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_role_presets(request):
    """获取预设角色列表"""
    try:
        presets = function_router_instance.get_role_presets()
        return Response({'roles': presets})
    except Exception as e:
        logger.error(f"Error getting role presets: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    """请求密码重置"""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        token = uuid.uuid4()
        PasswordResetToken.objects.create(user=user, token=token)
        # In a real app, you'd email this token.
        # send_mail(...)
        return Response({'message': 'Password reset email sent', 'token': str(token)}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """重置密码"""
    token = request.data.get('token')
    password = request.data.get('password')
    if not token or not password:
        return Response({'error': 'Token and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if reset_token.is_expired():
            return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
        user = reset_token.user
        user.set_password(password)
        user.save()
        reset_token.delete()
        return Response({'message': 'Password has been reset'}, status=status.HTTP_200_OK)
    except PasswordResetToken.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password_test(request):
    """测试环境的密码重置功能 - 直接通过用户名或邮箱重置密码"""
    identifier = request.data.get('identifier')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not identifier or not new_password or not confirm_password:
        return Response({'error': 'Identifier, new password and confirm password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != confirm_password:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 验证密码强度
        try:
            validate_password(new_password, user=None)
        except ValidationError as e:
            return Response({'error': f'Password invalid: {", ".join(e.messages)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 尝试按用户名查找用户
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            # 如果用户名不存在，尝试按邮箱查找
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                return Response({'error': 'User with this username or email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def available_models(request):
    """获取所有可用模型列表"""
    logger.info("Attempting to fetch available models.")
    try:
        logger.info("Calling EnhancedApiWrapper.get_available_models()")
        models = EnhancedApiWrapper.get_available_models()
        logger.info(f"Successfully fetched models: {models}")
        return Response(models)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"获取模型列表失败: {str(e)}")
        logger.error(f"详细错误信息: {error_traceback}")
        return Response(
            {"error": "获取模型列表失败", "detail": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ConversationViewSet(viewsets.ModelViewSet):
    """会话视图集"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise exceptions.PermissionDenied("用户未认证")
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        try:
            conversation = self.get_object()
            if conversation.user != request.user:
                return Response({'error': '无权访问此会话'}, status=status.HTTP_403_FORBIDDEN)
            messages = Message.objects.filter(conversation=conversation).order_by('created_at')
            serializer = MessageSerializer(messages, many=True)
            messages.filter(role='assistant', is_read=False).update(is_read=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"获取消息列表失败: {str(e)}")
            # 检查是否是对象不存在的错误
            if 'No Conversation matches the given query' in str(e) or 'does not exist' in str(e).lower():
                return Response({'error': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': '获取消息列表失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MessageViewSet(viewsets.ModelViewSet):
    """消息视图集"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """只返回属于当前用户的消息"""
        return Message.objects.filter(conversation__user=self.request.user)

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            return Response({"error": "所有字段都是必需的"}, status=status.HTTP_400_BAD_REQUEST)
        
        if password != confirm_password:
            return Response({"error": "两次输入的密码不一致"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "用户名已存在"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "邮箱已存在"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_password(password)
            user = User.objects.create_user(username=username, email=email, password=password)
            # UserProfile 会通过 post_save 信号自动创建，无需手动创建
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.tokens import RefreshToken

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            
            # 获取用户信息，确保头像字段在根级别
            try:
                profile = user.profile
                user_data = UserSerializer(user).data
                profile_data = UserProfileSerializer(profile, context={'request': request}).data
                user_data.update(profile_data)
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
                user_data = UserSerializer(user).data
                profile_data = UserProfileSerializer(profile, context={'request': request}).data
                user_data.update(profile_data)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data
            })
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_info(request):
    user = request.user
    try:
        profile = user.profile  # 使用正确的related_name
        user_data = UserSerializer(user).data
        profile_data = UserProfileSerializer(profile, context={'request': request}).data
        user_data.update(profile_data)
        return Response(user_data)
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=user)
        user_data = UserSerializer(user).data
        profile_data = UserProfileSerializer(profile, context={'request': request}).data
        user_data.update(profile_data)
        return Response(user_data)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_user_info(request):
    user = request.user
    try:
        profile = user.profile  # 使用正确的related_name
    except UserProfile.DoesNotExist:
        # 如果用户资料不存在，创建一个
        profile = UserProfile.objects.create(user=user)
    
    user_serializer = UserSerializer(user, data=request.data, partial=True)
    profile_serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    
    user_valid = user_serializer.is_valid()
    profile_valid = profile_serializer.is_valid()

    if user_valid and profile_valid:
        user_serializer.save()
        profile_serializer.save()
        user_data = user_serializer.data
        user_data.update(profile_serializer.data)
        return Response(user_data)
    else:
        errors = {}
        if not user_valid:
            errors.update(user_serializer.errors)
        if not profile_valid:
            errors.update(profile_serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """获取或更新用户个人资料"""
    user = request.user
    
    try:
        user_profile = user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    
    if request.method == 'GET':
        # 获取个人资料
        user_data = UserSerializer(user).data
        profile_data = UserProfileSerializer(user_profile).data
        user_data.update(profile_data)
        return Response(user_data)
    
    elif request.method == 'PUT':
        # 更新个人资料
        data = request.data
        
        # 更新用户基本信息
        if 'email' in data:
            user.email = data['email']
            user.save()
        
        # 更新用户资料信息
        if 'nickname' in data:
            user_profile.nickname = data['nickname']
        if 'bio' in data:
            user_profile.bio = data['bio']
        
        user_profile.save()
        
        return Response({'message': '个人资料保存成功'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    if 'avatar' in request.FILES:
        user_profile = request.user.profile
        # Delete old avatar if it exists
        if user_profile.avatar and os.path.exists(user_profile.avatar.path):
            os.remove(user_profile.avatar.path)

        user_profile.avatar = request.FILES['avatar']
        user_profile.save()

        # Return the new avatar URL
        return Response({'avatar_url': request.build_absolute_uri(user_profile.avatar.url)})
    return Response({'error': 'No avatar file found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_chat_image(request):
    """上传聊天图片，返回图片URL用于AI识别"""
    if 'image' in request.FILES:
        image_file = request.FILES['image']

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response({'error': '不支持的图片格式，请上传 JPG、PNG、GIF 或 WebP 格式的图片'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件大小（最大10MB）
        if image_file.size > 10 * 1024 * 1024:
            return Response({'error': '图片大小不能超过10MB'}, status=status.HTTP_400_BAD_REQUEST)

        # 保存图片到媒体目录
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os
        from datetime import datetime

        # 生成唯一文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 对于未登录用户，使用 'guest' 作为用户ID
        user_id = request.user.id if request.user.is_authenticated else 'guest'
        filename = f"chat_images/{user_id}/{timestamp}_{image_file.name}"

        # 保存文件
        file_path = default_storage.save(filename, ContentFile(image_file.read()))

        # 构建相对URL（用于Vite代理）
        image_url = default_storage.url(file_path)

        return Response({
            'image_url': image_url,
            'filename': image_file.name,
            'size': image_file.size
        })
    return Response({'error': 'No image file found'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== 用户设置 API ====================

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def user_settings(request):
    """获取或更新用户设置"""
    user_profile = request.user.profile
    
    if request.method == 'GET':
        return Response({
            'ai': {
                'qwenApiKey': user_profile.qwen_api_key or '',
                'deepseekApiKey': user_profile.deepseek_api_key or '',
                'doubaoApiKey': user_profile.doubao_api_key or '',
            },
            'preferences': {
                'theme': user_profile.theme or 'auto',
                'language': user_profile.language or 'zh-CN',
            },
            'privacy': {
                'saveChatHistory': user_profile.save_chat_history,
                'allowAnalytics': user_profile.allow_analytics,
            }
        })
    
    elif request.method == 'PUT':
        data = request.data
        
        # 更新 AI 设置
        if 'ai' in data:
            ai_settings = data['ai']
            user_profile.qwen_api_key = ai_settings.get('qwenApiKey', user_profile.qwen_api_key)
            user_profile.deepseek_api_key = ai_settings.get('deepseekApiKey', user_profile.deepseek_api_key)
            user_profile.doubao_api_key = ai_settings.get('doubaoApiKey', user_profile.doubao_api_key)
        
        # 更新外观设置
        if 'preferences' in data:
            pref_settings = data['preferences']
            user_profile.theme = pref_settings.get('theme', user_profile.theme)
            user_profile.language = pref_settings.get('language', user_profile.language)
        
        # 更新隐私设置
        if 'privacy' in data:
            privacy_settings = data['privacy']
            user_profile.save_chat_history = privacy_settings.get('saveChatHistory', user_profile.save_chat_history)
            user_profile.allow_analytics = privacy_settings.get('allowAnalytics', user_profile.allow_analytics)
        
        user_profile.save()
        return Response({'message': '设置保存成功'})


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def ai_settings(request):
    """更新 AI 设置"""
    user_profile = request.user.profile
    data = request.data
    
    user_profile.qwen_api_key = data.get('qwenApiKey', user_profile.qwen_api_key)
    user_profile.deepseek_api_key = data.get('deepseekApiKey', user_profile.deepseek_api_key)
    user_profile.doubao_api_key = data.get('doubaoApiKey', user_profile.doubao_api_key)
    user_profile.save()
    
    return Response({'message': 'AI设置保存成功'})


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def appearance_settings(request):
    """更新外观设置"""
    user_profile = request.user.profile
    data = request.data
    
    user_profile.theme = data.get('theme', user_profile.theme)
    user_profile.language = data.get('language', user_profile.language)
    user_profile.save()
    
    return Response({'message': '外观设置保存成功'})


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def privacy_settings(request):
    """更新隐私设置"""
    user_profile = request.user.profile
    data = request.data
    
    user_profile.save_chat_history = data.get('saveChatHistory', user_profile.save_chat_history)
    user_profile.allow_analytics = data.get('allowAnalytics', user_profile.allow_analytics)
    user_profile.save()
    
    return Response({'message': '隐私设置保存成功'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """修改密码（需要当前密码验证）"""
    logger.info(f"修改密码API被调用，用户: {request.user.username}")
    user = request.user
    data = request.data
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # 验证参数
    if not all([current_password, new_password, confirm_password]):
        return Response({'error': '请填写所有密码字段'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证当前密码
    if not user.check_password(current_password):
        return Response({'error': '当前密码不正确'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证新密码长度
    if len(new_password) < 6:
        return Response({'error': '新密码长度至少6个字符'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证两次密码是否一致
    if new_password != confirm_password:
        return Response({'error': '两次输入的新密码不一致'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证新密码是否与旧密码相同
    if current_password == new_password:
        return Response({'error': '新密码不能与当前密码相同'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({'message': '密码修改成功，请使用新密码重新登录'})
    except Exception as e:
        return Response({'error': f'密码修改失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


