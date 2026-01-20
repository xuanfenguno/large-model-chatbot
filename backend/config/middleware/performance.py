"""
性能监控中间件
用于诊断Django服务的高CPU占用问题
"""
import time
import threading
import psutil
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class PerformanceMiddleware(MiddlewareMixin):
    """性能监控中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_times = {}
        self.slow_requests = []
        self.start_monitoring()
    
    def start_monitoring(self):
        """启动性能监控线程"""
        def monitor_resources():
            while True:
                try:
                    # 检查CPU使用率
                    cpu_percent = psutil.cpu_percent(interval=5)
                    
                    # 检查内存使用率
                    memory = psutil.virtual_memory()
                    
                    # 如果CPU或内存使用率过高，记录警告
                    if cpu_percent > 80:
                        print(f"⚠️ CPU使用率过高: {cpu_percent}%")
                        self.log_slow_requests()
                    
                    if memory.percent > 85:
                        print(f"⚠️ 内存使用率过高: {memory.percent}%")
                    
                    # 检查是否有频繁的请求
                    self.check_frequent_requests()
                    
                except Exception as e:
                    print(f"性能监控错误: {e}")
                
                time.sleep(10)  # 每10秒检查一次
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        monitor_thread.start()
    
    def process_request(self, request):
        """处理请求前"""
        request.start_time = time.time()
        
        # 记录请求路径和时间
        path = request.path
        if path not in self.request_times:
            self.request_times[path] = []
        
        self.request_times[path].append(time.time())
        
        # 只保留最近1分钟的请求记录
        current_time = time.time()
        self.request_times[path] = [t for t in self.request_times[path] if current_time - t < 60]
        
        return None
    
    def process_response(self, request, response):
        """处理响应后"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # 记录慢请求
            if duration > 1.0:  # 超过1秒的请求
                slow_request_info = {
                    'path': request.path,
                    'method': request.method,
                    'duration': round(duration, 2),
                    'timestamp': time.time()
                }
                self.slow_requests.append(slow_request_info)
                
                # 只保留最近10个慢请求记录
                if len(self.slow_requests) > 10:
                    self.slow_requests = self.slow_requests[-10:]
                
                print(f"🐌 慢请求: {request.path} - {duration:.2f}s")
            
            # 记录请求统计
            if duration > 0.1:  # 超过100ms的请求都记录
                print(f"📊 请求: {request.path} - {duration:.3f}s")
        
        return response
    
    def check_frequent_requests(self):
        """检查频繁请求"""
        current_time = time.time()
        
        for path, times in self.request_times.items():
            # 检查最近30秒内的请求频率
            recent_requests = [t for t in times if current_time - t < 30]
            
            if len(recent_requests) > 10:  # 30秒内超过10次请求
                print(f"🚨 频繁请求警告: {path} - 30秒内{len(recent_requests)}次请求")
                
                # 建议优化措施
                if '/api/v1/conversations/' in path:
                    print("💡 建议: 添加会话列表缓存，减少数据库查询")
                elif '/api/v1/models/' in path:
                    print("💡 建议: 模型列表可以缓存，无需频繁查询")
    
    def log_slow_requests(self):
        """记录慢请求日志"""
        if self.slow_requests:
            print("\n📋 最近慢请求统计:")
            for req in self.slow_requests[-5:]:  # 显示最近5个慢请求
                print(f"  - {req['path']} ({req['method']}): {req['duration']}s")


class DatabaseQueryMiddleware(MiddlewareMixin):
    """数据库查询监控中间件"""
    
    def process_response(self, request, response):
        """处理响应后检查数据库查询"""
        from django.db import connection
        
        if hasattr(connection, 'queries') and connection.queries:
            query_count = len(connection.queries)
            query_time = sum(float(q['time']) for q in connection.queries)
            
            if query_count > 10:  # 超过10个查询
                print(f"🐌 数据库查询过多: {request.path} - {query_count}次查询，耗时{query_time:.3f}s")
                
                # 显示最慢的查询
                slow_queries = sorted(connection.queries, key=lambda x: float(x['time']), reverse=True)[:3]
                print("最慢的查询:")
                for i, query in enumerate(slow_queries):
                    print(f"  {i+1}. {query['time']}s: {query['sql'][:100]}...")
        
        return response