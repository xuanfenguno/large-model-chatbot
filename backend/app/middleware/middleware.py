"""
统一错误处理中间件
"""
import json
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import ValidationError
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
import traceback


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    统一错误处理中间件，捕获所有异常并返回标准格式的错误响应
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)
        super().__init__(get_response)

    def process_exception(self, request, exception):
        """
        处理视图中发生的异常
        """
        # 记录错误日志
        self.logger.error(
            f"Error in {request.method} {request.path}: {str(exception)}",
            extra={
                'request': request,
                'exception': exception,
                'traceback': traceback.format_exc()
            }
        )
        
        # 根据异常类型返回相应的错误响应
        if isinstance(exception, ValidationError):
            return JsonResponse({
                'error': '数据验证失败',
                'details': exception.detail if hasattr(exception, 'detail') else str(exception),
                'success': False
            }, status=400)
        
        elif isinstance(exception, PermissionDenied):
            return JsonResponse({
                'error': '权限不足',
                'details': '您没有执行此操作的权限',
                'success': False
            }, status=403)
        
        elif isinstance(exception, ObjectDoesNotExist):
            return JsonResponse({
                'error': '资源不存在',
                'details': '请求的资源未找到',
                'success': False
            }, status=404)
        
        elif isinstance(exception, ValueError):
            return JsonResponse({
                'error': '参数错误',
                'details': str(exception),
                'success': False
            }, status=400)
        
        elif isinstance(exception, KeyError):
            return JsonResponse({
                'error': '缺少必要参数',
                'details': f'缺少参数: {str(exception)}',
                'success': False
            }, status=400)
        
        else:
            # 其他未预期的错误
            return JsonResponse({
                'error': '服务器内部错误',
                'details': '服务器遇到意外错误，请稍后重试',
                'success': False
            }, status=500)


def error_404_view(request, exception=None):
    """自定义404页面"""
    return JsonResponse({
        'error': '页面未找到',
        'details': '请求的资源不存在',
        'success': False
    }, status=404)


def error_500_view(request):
    """自定义500页面"""
    return JsonResponse({
        'error': '服务器内部错误',
        'details': '服务器遇到意外错误，请稍后重试',
        'success': False
    }, status=500)


def error_400_view(request, exception=None):
    """自定义400页面"""
    return JsonResponse({
        'error': '请求错误',
        'details': '请求参数有误',
        'success': False
    }, status=400)


def error_403_view(request, exception=None):
    """自定义403页面"""
    return JsonResponse({
        'error': '权限拒绝',
        'details': '您没有访问此资源的权限',
        'success': False
    }, status=403)