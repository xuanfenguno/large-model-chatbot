"""
统一错误处理中间件
处理应用程序中的异常并返回适当的响应
"""

import json
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    统一错误处理中间件
    """
    
    def process_exception(self, request, exception):
        """
        处理视图中抛出的异常
        """
        # 记录错误日志
        logger.error(f"Error in {request.path}: {str(exception)}", exc_info=True)
        
        # 对于API请求，返回JSON格式的错误响应
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': '服务器内部错误',
                'message': str(exception) if isinstance(exception, (ValueError, TypeError, AttributeError)) else 'An error occurred'
            }, status=500)
        
        # 对于其他请求，让Django默认处理
        return None