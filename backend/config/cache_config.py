"""
Redis缓存配置和缓存优化
"""
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.redis import RedisCache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from functools import wraps
import hashlib
import json


# Redis缓存配置
CACHE_CONFIG = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'chatbot',
        'TIMEOUT': 60 * 15  # 默认15分钟
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'chatbot_sessions',
        'TIMEOUT': 60 * 60 * 24  # 24小时
    },
    'api_cache': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379/3'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'chatbot_api',
        'TIMEOUT': 60 * 5  # 5分钟
    }
}


def cache_function(timeout=300):
    """
    函数级缓存装饰器
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"func_{func.__name__}_{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is None:
                # 执行函数并缓存结果
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def get_cached_user_profile(user_id):
    """
    获取缓存的用户配置
    """
    cache_key = f"user_profile_{user_id}"
    profile = cache.get(cache_key)
    if profile is None:
        from chatbot.models import UserProfile
        try:
            user_profile = UserProfile.objects.select_related('user').get(user_id=user_id)
            # 只缓存必要的字段
            profile = {
                'id': user_profile.id,
                'phone': user_profile.phone,
                'openai_api_key': user_profile.openai_api_key,
                'qwen_api_key': user_profile.qwen_api_key,
                'gemini_api_key': user_profile.gemini_api_key,
                'model_preferences': {
                    'default_model': getattr(user_profile, 'default_model', 'gpt-3.5-turbo'),
                    'temperature': getattr(user_profile, 'temperature', 0.7),
                },
                'updated_at': user_profile.updated_at.isoformat() if user_profile.updated_at else None
            }
            cache.set(cache_key, profile, 60 * 60)  # 缓存1小时
        except UserProfile.DoesNotExist:
            profile = None
            cache.set(cache_key, profile, 60 * 15)  # 缓存15分钟，避免重复查询不存在的用户
    return profile


def get_cached_conversations(user_id, limit=20):
    """
    获取缓存的会话列表
    """
    cache_key = f"user_conversations_{user_id}_limit_{limit}"
    conversations = cache.get(cache_key)
    if conversations is None:
        from chatbot.models import Conversation
        conversations_qs = Conversation.objects.filter(user_id=user_id).order_by('-updated_at')[:limit]
        conversations = [
            {
                'id': conv.id,
                'title': conv.title,
                'model': conv.model,
                'mode': conv.mode,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': conv.messages.count() if hasattr(conv, 'messages') else 0
            }
            for conv in conversations_qs
        ]
        cache.set(cache_key, conversations, 60 * 5)  # 缓存5分钟
    return conversations


def invalidate_user_cache(user_id):
    """
    清除用户的缓存
    """
    # 清除用户配置缓存
    cache.delete(f"user_profile_{user_id}")
    # 清除用户会话缓存
    cache.delete_pattern(f"user_conversations_{user_id}*")


def get_cached_api_response(api_key, endpoint, params=None, timeout=300):
    """
    缓存API响应
    """
    cache_key = f"api_response_{hashlib.md5((api_key + endpoint + str(params or {})).encode()).hexdigest()}"
    response = cache.get(cache_key)
    if response is None:
        # 这里应该是实际的API调用
        # response = call_external_api(api_key, endpoint, params)
        # 为了演示目的，这里返回None
        response = None
        if response:
            cache.set(cache_key, response, timeout)
    return response


# 常用的缓存键生成器
def generate_cache_key(prefix, *args, **kwargs):
    """
    生成标准化的缓存键
    """
    key_parts = [prefix]
    key_parts.extend([str(arg) for arg in args])
    if kwargs:
        key_parts.append(json.dumps(kwargs, sort_keys=True))
    return "_".join(key_parts)


# 缓存清理工具
def clear_all_chatbot_cache():
    """
    清除所有chatbot相关的缓存
    """
    cache.delete_pattern("chatbot:*")
    cache.delete_pattern("func_*")
    cache.delete_pattern("user_profile_*")
    cache.delete_pattern("user_conversations_*")
    cache.delete_pattern("api_response_*")


# 缓存健康检查
def check_cache_health():
    """
    检查缓存服务健康状态
    """
    try:
        cache.set("health_check", "ok", 10)
        result = cache.get("health_check")
        return result == "ok"
    except:
        return False