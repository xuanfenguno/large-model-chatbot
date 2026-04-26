"""
系统诊断脚本 - 检查所有关键配置和依赖
确保系统启动时所有组件正常工作
"""
import os
import sys
import importlib
from pathlib import Path

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
import requests

class SystemDiagnostics:
    """系统诊断工具"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
    
    def run_all_checks(self):
        """运行所有诊断检查"""
        print("=" * 60)
        print("系统诊断工具 - 开始检查")
        print("=" * 60)
        
        self.check_python_version()
        self.check_django_setup()
        self.check_database_connection()
        self.check_redis_connection()
        self.check_api_keys()
        self.check_required_packages()
        self.check_knowledge_base()
        self.check_cors_settings()
        
        self.print_report()
        
        return len(self.issues) == 0
    
    def check_python_version(self):
        """检查Python版本"""
        print("\n[1/8] 检查Python版本...")
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.successes.append(f"Python版本: {version.major}.{version.minor}.{version.micro}")
            print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.issues.append(f"Python版本过低: {version.major}.{version.minor}，需要3.8+")
            print(f"  ❌ Python版本过低")
    
    def check_django_setup(self):
        """检查Django配置"""
        print("\n[2/8] 检查Django配置...")
        try:
            # 检查SECRET_KEY
            if settings.SECRET_KEY and 'django-insecure' not in settings.SECRET_KEY:
                self.successes.append("Django SECRET_KEY已配置")
                print("  ✅ SECRET_KEY已配置")
            else:
                self.warnings.append("使用默认的SECRET_KEY，生产环境需要修改")
                print("  ⚠️ 使用默认SECRET_KEY")
            
            # 检查DEBUG模式
            if settings.DEBUG:
                self.successes.append("DEBUG模式已启用（开发环境）")
                print("  ✅ DEBUG模式已启用")
            else:
                self.warnings.append("DEBUG模式已关闭")
                print("  ⚠️ DEBUG模式已关闭")
                
        except Exception as e:
            self.issues.append(f"Django配置错误: {str(e)}")
            print(f"  ❌ Django配置错误: {str(e)}")
    
    def check_database_connection(self):
        """检查数据库连接"""
        print("\n[3/8] 检查数据库连接...")
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            
            db_engine = settings.DATABASES['default']['ENGINE']
            db_name = settings.DATABASES['default']['NAME']
            self.successes.append(f"数据库连接成功: {db_engine}")
            print(f"  ✅ 数据库连接成功")
            
        except Exception as e:
            self.issues.append(f"数据库连接失败: {str(e)}")
            print(f"  ❌ 数据库连接失败: {str(e)}")
    
    def check_redis_connection(self):
        """检查Redis连接"""
        print("\n[4/8] 检查Redis连接...")
        try:
            import redis
            redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)
            redis_client.ping()
            self.successes.append("Redis连接成功")
            print("  ✅ Redis连接成功")
        except ImportError:
            self.warnings.append("Redis未安装，将使用内存缓存")
            print("  ⚠️ Redis未安装，使用内存缓存")
        except Exception as e:
            self.warnings.append(f"Redis连接失败: {str(e)}，将使用内存缓存")
            print(f"  ⚠️ Redis连接失败，将使用内存缓存")
    
    def check_api_keys(self):
        """检查API密钥配置"""
        print("\n[5/8] 检查API密钥配置...")
        
        api_keys = {
            'QWEN_API_KEY': settings.LLM_CONFIG.get('QWEN_API_KEY'),
            'OPENAI_API_KEY': settings.LLM_CONFIG.get('OPENAI_API_KEY'),
            'GEMINI_API_KEY': settings.LLM_CONFIG.get('GEMINI_API_KEY'),
            'DEEPSEEK_API_KEY': settings.LLM_CONFIG.get('DEEPSEEK_API_KEY'),
            'KIMI_API_KEY': settings.LLM_CONFIG.get('KIMI_API_KEY'),
        }
        
        available_providers = []
        for key_name, key_value in api_keys.items():
            if key_value and key_value.strip():
                available_providers.append(key_name)
                print(f"  ✅ {key_name} 已配置")
            else:
                print(f"  ❌ {key_name} 未配置")
        
        if available_providers:
            self.successes.append(f"已配置API密钥: {', '.join(available_providers)}")
        else:
            self.issues.append("未配置任何API密钥，系统将使用模拟响应")
            print("\n  ⚠️ 警告: 未配置任何API密钥")
    
    def check_required_packages(self):
        """检查必需的Python包"""
        print("\n[6/8] 检查必需的Python包...")
        
        required_packages = {
            'django': 'Django',
            'rest_framework': 'Django REST Framework',
            'corsheaders': 'CORS Headers',
            'requests': 'Requests',
            'PIL': 'Pillow',
            'dotenv': 'python-dotenv',
        }
        
        optional_packages = {
            'chromadb': 'ChromaDB (知识库)',
            'sentence_transformers': 'Sentence Transformers (向量模型)',
            'redis': 'Redis',
            'celery': 'Celery (异步任务)',
        }
        
        # 检查必需包
        for package, name in required_packages.items():
            try:
                importlib.import_module(package)
                self.successes.append(f"{name} 已安装")
                print(f"  ✅ {name}")
            except ImportError:
                self.issues.append(f"{name} 未安装")
                print(f"  ❌ {name} 未安装")
        
        # 检查可选包（使用find_spec避免实际导入，速度更快）
        for package, name in optional_packages.items():
            try:
                spec = importlib.util.find_spec(package)
                if spec is not None:
                    self.successes.append(f"{name} 已安装")
                    print(f"  ✅ {name}")
                else:
                    self.warnings.append(f"{name} 未安装")
                    print(f"  ⚠️ {name} 未安装")
            except (ModuleNotFoundError, ValueError):
                self.warnings.append(f"{name} 未安装")
                print(f"  ⚠️ {name} 未安装")
            except Exception as e:
                self.warnings.append(f"{name} 检查失败")
                print(f"  ⚠️ {name} 检查失败: {str(e)[:50]}")
    
    def check_knowledge_base(self):
        """检查知识库"""
        print("\n[7/8] 检查知识库...")
        try:
            import chromadb
            chroma_path = "./chroma_data"
            
            if os.path.exists(chroma_path):
                self.successes.append("知识库数据目录存在")
                print("  ✅ 知识库数据目录存在")
            else:
                self.warnings.append("知识库数据目录不存在，将自动创建")
                print("  ⚠️ 知识库数据目录不存在")
                
        except ImportError:
            self.warnings.append("ChromaDB未安装，知识库功能不可用")
            print("  ⚠️ ChromaDB未安装")
        except Exception as e:
            self.warnings.append(f"知识库检查失败: {str(e)}")
            print(f"  ⚠️ 知识库检查失败: {str(e)}")
    
    def check_cors_settings(self):
        """检查CORS配置"""
        print("\n[8/8] 检查CORS配置...")
        try:
            if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and settings.CORS_ALLOW_ALL_ORIGINS:
                self.successes.append("CORS允许所有来源（开发环境）")
                print("  ✅ CORS配置正确")
            elif hasattr(settings, 'CORS_ALLOWED_ORIGINS') and settings.CORS_ALLOWED_ORIGINS:
                self.successes.append("CORS已配置允许的源")
                print("  ✅ CORS已配置")
            else:
                self.warnings.append("CORS配置可能有问题")
                print("  ⚠️ CORS配置需要检查")
        except Exception as e:
            self.issues.append(f"CORS配置错误: {str(e)}")
            print(f"  ❌ CORS配置错误: {str(e)}")
    
    def print_report(self):
        """打印诊断报告"""
        print("\n" + "=" * 60)
        print("诊断报告")
        print("=" * 60)
        
        if self.successes:
            print(f"\n✅ 通过检查 ({len(self.successes)}):")
            for success in self.successes:
                print(f"  • {success}")
        
        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.issues:
            print(f"\n❌ 错误 ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  • {issue}")
        
        print("\n" + "=" * 60)
        if self.issues:
            print("⚠️  发现错误，请在启动前修复以上问题")
        else:
            print("✅ 所有检查通过，系统可以正常启动")
        print("=" * 60)


if __name__ == '__main__':
    diagnostics = SystemDiagnostics()
    success = diagnostics.run_all_checks()
    
    # 返回退出码
    sys.exit(0 if success else 1)
