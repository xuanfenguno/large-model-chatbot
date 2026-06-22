from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
import hashlib
import re
import logging

logger = logging.getLogger(__name__)

# 导入安全配置
try:
    from ..security_config import IP_BLACKLIST_CONFIG, INPUT_VALIDATION_CONFIG
except ImportError:
    # 默认配置
    IP_BLACKLIST_CONFIG = {
        'enable_ip_blacklist': True,
        'blacklist_duration_minutes': 1440,  # 24小时
    }
    INPUT_VALIDATION_CONFIG = {
        'dangerous_patterns': [
            r'<script', r'javascript:', r'on\w+\s*=', r'eval\(', r'document\.cookie',
            r'window\.location', r'expression\(', r'<iframe', r'<object', r'<embed'
        ]
    }

# IP 黑名单
BLACKLISTED_IPS = set()

def clear_blacklisted_ips():
    """清除所有被列入黑名单的IP地址"""
    global BLACKLISTED_IPS
    BLACKLISTED_IPS.clear()
    # 也清除缓存中的相关记录
    try:
        from django.core.cache import cache
        cache.clear()
    except:
        pass

# 危险请求模式
DANGEROUS_PATTERNS = INPUT_VALIDATION_CONFIG.get('dangerous_patterns', [
    r'<script', r'javascript:', r'on\w+\s*=', r'eval\(', r'document\.cookie',
    r'window\.location', r'expression\(', r'<iframe', r'<object', r'<embed'
])


def is_dangerous_content(request):
    """
    检查请求是否包含危险内容
    """
    # 检查请求体
    if hasattr(request, 'body') and request.body:
        body_str = request.body.decode('utf-8', errors='ignore').lower()
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, body_str):
                return True, f"检测到危险内容: {pattern}"
    
    # 检查请求头
    for header_name, header_value in request.META.items():
        if isinstance(header_value, str) and any(re.search(pattern, header_value.lower()) for pattern in DANGEROUS_PATTERNS):
            return True, f"请求头 {header_name} 包含危险内容"
    
    # 检查GET参数
    for param_name, param_value in request.GET.items():
        if isinstance(param_value, str) and any(re.search(pattern, param_value.lower()) for pattern in DANGEROUS_PATTERNS):
            return True, f"GET参数 {param_name} 包含危险内容"
    
    # 检查POST参数
    for param_name, param_value in request.POST.items():
        if isinstance(param_value, str) and any(re.search(pattern, param_value.lower()) for pattern in DANGEROUS_PATTERNS):
            return True, f"POST参数 {param_name} 包含危险内容"
    
    return False, ""


def rate_limit(max_requests=10, window_size=60, block_malicious=True):
    """
    增强版速率限制装饰器
    :param max_requests: 时间窗口内最大请求数
    :param window_size: 时间窗口大小（秒）
    :param block_malicious: 是否阻止恶意请求
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 获取客户端IP
            ip_address = get_client_ip(request)
            
            # 检查IP是否在黑名单中
            if ip_address in BLACKLISTED_IPS:
                logger.warning(f"Blocked blacklisted IP: {ip_address}")
                return JsonResponse({
                    'error': '您的IP已被加入黑名单，请联系管理员',
                }, status=403)
            
            # 检查是否包含恶意内容
            if block_malicious:
                is_dangerous, reason = is_dangerous_content(request)
                if is_dangerous:
                    logger.warning(f"Malicious content detected from {ip_address}: {reason}")
                    # 将IP加入临时黑名单
                    BLACKLISTED_IPS.add(ip_address)
                    return JsonResponse({
                        'error': '检测到恶意内容，请求被拒绝',
                    }, status=400)
            
            # 创建唯一标识符（基于IP地址和视图函数名）
            view_name = f"{view_func.__module__}.{view_func.__name__}"
            key = f"rate_limit:{ip_address}:{view_name}"
            
            # 获取当前窗口内的请求数
            current_requests = cache.get(key, [])
            
            # 移除过期的请求记录
            now = timezone.now()
            current_requests = [req_time for req_time in current_requests 
                              if now - req_time < timedelta(seconds=window_size)]
            
            # 检查是否超过限制
            if len(current_requests) >= max_requests:
                logger.warning(f"Rate limit exceeded for IP: {ip_address}, View: {view_name}")
                return JsonResponse({
                    'error': '请求过于频繁，请稍后再试',
                    'retry_after': window_size
                }, status=429)
            
            # 添加当前请求时间
            current_requests.append(now)
            cache.set(key, current_requests, timeout=window_size)
            
            # 执行原始视图函数
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def get_client_ip(request):
    """获取客户端真实IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def apply_rate_limits():
    """应用API速率限制的便捷函数"""
    pass