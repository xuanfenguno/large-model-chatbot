#!/usr/bin/env python
"""
优化内存使用的Django开发服务器
"""
import os
import sys
import gc
from django.core.management import execute_from_command_line

# 添加内存优化配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 内存优化配置
import django
from django.conf import settings

# 配置内存优化选项
if not settings.DEBUG:
    # 生产环境优化
    os.environ['PYTHONHASHSEED'] = '0'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# 导入Django设置后配置
from django.core.wsgi import get_wsgi_application

# 内存优化函数
def optimize_memory():
    """优化内存使用"""
    # 禁用不必要的中间件（开发环境）
    if settings.DEBUG:
        # 移除一些开发环境不需要的中间件
        optimized_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'corsheaders.middleware.CorsMiddleware',
        ]
        
        # 设置优化后的中间件
        settings.MIDDLEWARE = optimized_middleware
    
    # 配置数据库连接池（如果使用数据库）
    if hasattr(settings, 'DATABASES'):
        for db_name in settings.DATABASES:
            settings.DATABASES[db_name]['CONN_MAX_AGE'] = 60  # 减少连接保持时间
    
    # 强制垃圾回收
    gc.collect()

if __name__ == '__main__':
    # 执行内存优化
    optimize_memory()
    
    # 启动优化后的服务器
    execute_from_command_line(['manage.py', 'runserver', '--noreload', '--nothreading'])
    
    # 定期清理内存
    import threading
    import time
    
    def memory_cleaner():
        """定期清理内存"""
        while True:
            time.sleep(60)  # 每分钟清理一次
            gc.collect()
    
    # 启动内存清理线程
    cleaner_thread = threading.Thread(target=memory_cleaner, daemon=True)
    cleaner_thread.start()