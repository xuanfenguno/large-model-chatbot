#!/usr/bin/env python
"""
内存优化的Django服务器启动脚本
"""
import os
import sys
import gc
import psutil

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 内存监控函数
def monitor_memory():
    """监控内存使用"""
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    return memory_mb

def optimize_django_memory():
    """优化Django内存使用"""
    import django
    from django.conf import settings
    
    # 配置优化选项
    if settings.DEBUG:
        # 开发环境优化
        os.environ['PYTHONOPTIMIZE'] = '1'
        
        # 减少日志级别
        import logging
        logging.getLogger('django').setLevel(logging.WARNING)
        
        # 禁用SQL日志
        logging.getLogger('django.db.backends').setLevel(logging.ERROR)
    
    # 强制垃圾回收
    gc.collect()

if __name__ == '__main__':
    print("🚀 启动内存优化的Django服务器...")
    
    # 初始内存检查
    initial_memory = monitor_memory()
    print(f"📊 初始内存使用: {initial_memory:.2f} MB")
    
    # 执行内存优化
    optimize_django_memory()
    
    # 导入Django并启动服务器
    try:
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        
        # 使用优化的启动参数
        args = [
            'manage.py', 'runserver', 
            '--noreload',           # 禁用自动重载
            '--nothreading',        # 禁用多线程
            '--verbosity', '1',     # 减少日志输出
            '127.0.0.1:8000'
        ]
        
        print("✅ 内存优化完成，启动服务器...")
        execute_from_command_line(args)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)