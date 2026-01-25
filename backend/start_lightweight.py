#!/usr/bin/env python
"""
轻量级Django服务器启动脚本 - 最小内存占用
"""
import os
import sys
import gc

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 最小化内存配置
def minimize_memory_usage():
    """最小化内存使用"""
    # 禁用Python字节码生成
    sys.dont_write_bytecode = True
    
    # 设置环境变量优化
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['PYTHONOPTIMIZE'] = '1'
    
    # 导入Django前优化
    import django
    from django.conf import settings
    
    # 临时禁用一些功能来减少内存
    if settings.DEBUG:
        # 开发环境：禁用一些中间件
        settings.MIDDLEWARE = [
            'django.middleware.common.CommonMiddleware',
            'corsheaders.middleware.CorsMiddleware',
        ]
        
        # 禁用模板调试
        settings.TEMPLATES[0]['OPTIONS']['debug'] = False
        
        # 减少日志输出
        import logging
        logging.getLogger('django').setLevel(logging.ERROR)
    
    # 强制垃圾回收
    for i in range(3):
        gc.collect()

if __name__ == '__main__':
    print("🚀 启动轻量级Django服务器（最小内存占用）...")
    
    # 执行内存最小化
    minimize_memory_usage()
    
    try:
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        
        # 使用最轻量的启动参数
        args = [
            'manage.py', 'runserver',
            '--noreload',           # 禁用自动重载（节省内存）
            '--nothreading',        # 禁用多线程（减少并发内存）
            '--verbosity', '0',     # 最小日志输出
            '--insecure',           # 禁用静态文件服务
            '127.0.0.1:8000'
        ]
        
        print("✅ 轻量级配置完成，启动服务器...")
        print("💡 提示：此模式禁用了一些开发功能以节省内存")
        
        execute_from_command_line(args)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)