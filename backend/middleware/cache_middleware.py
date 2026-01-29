"""
缓存中间件，用于优化API响应时间
"""
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import hashlib
import time
import logging

logger = logging.getLogger(__name__)


class APICacheMiddleware(MiddlewareMixin):
    """
    API缓存中间件
    """
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        # 只对GET请求进行缓存
        if request.method != 'GET':
            return None
        
        # 检查是否应该跳过缓存
        if self.should_skip_cache(request):
            return None
        
        # 生成缓存键
        cache_key = self.generate_cache_key(request)
        
        # 尝试从缓存获取响应
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for {request.path}")
            return JsonResponse(cached_response)
        
        return None

    def process_response(self, request, response):
        # 只缓存成功的GET请求
        if (request.method == 'GET' and 
            response.status_code == 200 and 
            not self.should_skip_cache(request)):
            
            # 生成缓存键
            cache_key = self.generate_cache_key(request)
            
            # 只缓存JSON响应
            if response.get('Content-Type', '').startswith('application/json'):
                # 提取响应数据
                import json
                try:
                    response_data = json.loads(response.content.decode('utf-8'))
                    # 设置缓存，有效期5分钟
                    cache_timeout = self.get_cache_timeout(request)
                    cache.set(cache_key, response_data, cache_timeout)
                    logger.info(f"Cache set for {request.path} with timeout {cache_timeout}")
                except json.JSONDecodeError:
                    pass  # 如果不是JSON响应，则不缓存
        
        return response

    def generate_cache_key(self, request):
        """
        生成缓存键
        """
        path = request.path
        query_params = str(sorted(request.GET.items()))
        user_id = getattr(request.user, 'id', 'anonymous')
        
        cache_string = f"{path}:{query_params}:{user_id}".encode('utf-8')
        return f"api_cache:{hashlib.md5(cache_string).hexdigest()}"

    def should_skip_cache(self, request):
        """
        判断是否应该跳过缓存
        """
        # 如果请求头包含特定标识，则跳过缓存
        if request.META.get('HTTP_CACHE_CONTROL') == 'no-cache':
            return True
        
        # 如果路径包含实时数据，则跳过缓存
        no_cache_paths = [
            '/api/v1/chat/stream/',  # 流式聊天API
            '/api/v1/user/profile/',  # 实时用户资料
            '/api/v1/realtime/',     # 实时API
        ]
        
        return any(request.path.startswith(path) for path in no_cache_paths)

    def get_cache_timeout(self, request):
        """
        根据请求路径返回不同的缓存超时时间
        """
        path = request.path
        
        # 个人资料页缓存时间短一些（5分钟）
        if '/api/v1/user/' in path:
            return 60 * 5
        
        # 静态数据可以缓存更长时间（1小时）
        if '/api/v1/config/' in path:
            return 60 * 60
        
        # 默认缓存时间（5分钟）
        return 60 * 5


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    性能监控中间件
    """
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # 记录慢请求
            if duration > 1.0:  # 超过1秒的请求
                logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
            
            # 添加性能头部（仅开发环境）
            if response.get('Content-Type', '').startswith('application/json'):
                response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response


class QueryCountMiddleware(MiddlewareMixin):
    """
    查询计数中间件，用于检测N+1查询问题
    """
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        from django.db import connection
        request.init_query_count = len(connection.queries)
        return None

    def process_response(self, request, response):
        from django.db import connection
        final_query_count = len(connection.queries)
        query_count = final_query_count - getattr(request, 'init_query_count', 0)
        
        # 如果查询数量过多，记录警告
        if query_count > 20:  # 阈值可根据需要调整
            logger.warning(f"High query count: {query_count} queries for {request.path}")
            # 记录具体的查询（仅在开发环境）
            if hasattr(request, 'init_query_count'):
                for query in connection.queries[request.init_query_count:]:
                    logger.debug(f"Query: {query['sql'][:100]}...")
        
        return response