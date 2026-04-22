from django.shortcuts import render
from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from .models import Conversation, Message, PasswordResetToken, UserProfile
from .serializers import ConversationSerializer, MessageSerializer, PasswordResetTokenSerializer, UserSerializer, UserProfileSerializer
from django.contrib.auth import authenticate, login, logout
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

        # 创建API实例
        api_instance = EnhancedApiWrapper.create_api_instance(model)

        try:
            result = api_instance.send_message(
                message=message_content,
                config={
                    'model': model,
                    'history': history[:-1] if history else [],
                    'temperature': 0.7,
                    'max_tokens': 2000,
                    'top_p': 0.9
                }
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
    conversation_id = request.data.get('conversation_id')
    message_content = request.data.get('message')
    image_url = request.data.get('image_url')
    model = request.data.get('model', 'gpt-3.5-turbo')

    # 调试日志
    logger.info(f"stream_chat 被调用 - image_url: {image_url}, model: {model}")

    # 如果上传了图片但当前模型不支持视觉，自动切换到视觉模型
    vision_models = ['qwen-vl-plus', 'qwen-vl-max', 'gpt-4-vision', 'gpt-4o', 'claude-3-opus', 'claude-3-sonnet']
    if image_url and model not in vision_models:
        # 尝试使用 qwen-vl-plus 作为默认视觉模型
        original_model = model
        model = 'qwen-vl-plus'
        logger.info(f"检测到图片但模型 {original_model} 不支持视觉，自动切换到 {model}")

    try:
        if conversation_id:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        else:
            title = message_content[:50] if message_content else "New Conversation"
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
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        for msg in messages:
            if msg.role == 'user':
                content = [{"type": "text", "text": msg.content}]
                if msg.image_url:
                    content.append({"type": "image_url", "image_url": {"url": msg.image_url}})
                history.append({"role": "user", "content": content if len(content) > 1 else content[0]['text']})
            elif msg.role == 'assistant':
                history.append({"role": "assistant", "content": msg.content})

        # EnhancedApiWrapper 不需要用户参数，直接使用静态方法
        pass  # 删除这行，因为我们不需要创建api_wrapper实例
        # 我们可以直接使用EnhancedApiWrapper.create_api_instance来创建API实例
        api_instance = EnhancedApiWrapper.create_api_instance(model)

        def stream_response_generator():
            full_response = ""
            try:
                # 立即返回一个初始消息，防止客户端超时
                yield f"data: {json.dumps({'content': ''})}" + "\n\n"
                
                # 在发送消息前，先检查知识库
                knowledge_context = ""
                try:
                    # 尝试从知识库中检索相关信息
                    from .utils.knowledge_base import knowledge_base_manager
                    if knowledge_base_manager.client is not None:
                        search_results = knowledge_base_manager.search(message_content, n_results=3)
                        if search_results and search_results.get('documents'):
                            # 将知识库检索结果整合为上下文
                            kb_docs = search_results['documents'][0]  # 取第一个结果的所有文档
                            if kb_docs:
                                knowledge_context = "基于知识库的相关信息：\n" + "\n".join(kb_docs[:2]) + "\n\n"
                except Exception as kb_error:
                    logger.warning(f"知识库检索失败: {str(kb_error)}")
                    # 知识库检索失败不影响主要功能，继续执行

                # 准备发送给AI的消息，包含知识库上下文
                enhanced_message = knowledge_context + message_content if knowledge_context else message_content

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
                        for content_chunk in api_instance.send_message_stream(
                            message=current_message_content,
                            config={
                                'model': model,
                                'history': history[:-1] if history else [],
                                'temperature': 0.7,
                                'max_tokens': 2000,
                                'top_p': 0.9
                            }
                        ):
                            full_response += content_chunk
                            # 逐块返回内容
                            yield f"data: {json.dumps({'content': content_chunk})}" + "\n\n"
                    else:
                        # 回退到非流式方式
                        result = api_instance.send_message(
                            message=current_message_content,
                            config={
                                'model': model,
                                'history': history[:-1] if history else [],
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
                logger.error(f"Streaming chat error: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}" + "\n\n"

        response = StreamingHttpResponse(stream_response_generator(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response

    except Conversation.DoesNotExist:
        return Response({'error': '会话不存在或不属于当前用户'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Stream chat setup error: {str(e)}")
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

    if not feature_name or not user_input:
        return Response({'error': 'Feature name and user input are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 将 feature_name 作为用户输入的一部分传入 route_function
        full_input = f"{feature_name} {user_input}".strip()
        response_content = function_router_instance.route_function(full_input, model=model, language=language, image_url=image_url)
        return Response({'result': response_content})
    except Exception as e:
        logger.error(f"Error in function router: {e}")
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
        models = EnhancedApiWrapper.get_available_models()
        logger.info(f"Successfully fetched models: {models}")
        return Response(models)
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return Response({"error": "获取模型列表失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        except Conversation.DoesNotExist:
            return Response({'error': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"获取消息列表失败: {str(e)}")
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
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
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
@permission_classes([permissions.IsAuthenticated])
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
        filename = f"chat_images/{request.user.id}/{timestamp}_{image_file.name}"

        # 保存文件
        file_path = default_storage.save(filename, ContentFile(image_file.read()))

        # 构建完整URL
        image_url = request.build_absolute_uri(default_storage.url(file_path))

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


