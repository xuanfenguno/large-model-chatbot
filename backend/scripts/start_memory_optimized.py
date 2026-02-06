#!/usr/bin/env python
"""
内存优化的Django服务器启动脚本 - 修复版
"""
import os
import sys
import gc

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def optimize_memory_settings():
    """优化内存设置，但不破坏Django功能"""
    import django
    from django.conf import settings
    
    # 设置优化环境变量
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['PYTHONOPTIMIZE'] = '1'
    
    # 减少日志输出（节省内存）
    import logging
    logging.getLogger('django').setLevel(logging.WARNING)
    logging.getLogger('django.db.backends').setLevel(logging.ERROR)
    
    # 配置数据库连接优化
    if hasattr(settings, 'DATABASES'):
        for db_name in settings.DATABASES:
            settings.DATABASES[db_name]['CONN_MAX_AGE'] = 30  # 减少连接保持时间
    
    # 强制垃圾回收
    for i in range(3):
        gc.collect()

if __name__ == '__main__':
    print("🚀 启动内存优化的Django服务器...")
    
    # 执行内存优化
    optimize_memory_settings()
    
    try:
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        
        # 使用优化的启动参数（保持功能完整）
        args = [
            'manage.py', 'runserver',
            '--noreload',           # 禁用自动重载（节省内存）
            '--verbosity', '1',     # 减少日志输出
            '127.0.0.1:8000'
        ]
        
        print("✅ 内存优化完成，启动服务器...")
        print("💡 提示：此模式保持Django功能完整，但优化了内存使用")
        
        execute_from_command_line(args)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)