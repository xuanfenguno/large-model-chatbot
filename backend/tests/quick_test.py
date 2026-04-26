"""
快速测试脚本 - 验证后端API是否正常工作
运行: python quick_test.py
"""
import os
import sys
import requests

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def test_env_file():
    """测试.env文件配置"""
    print("=" * 60)
    print("测试1: 检查.env文件配置")
    print("=" * 60)
    
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(env_path):
        print("❌ .env文件不存在")
        return False
    
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键配置
    checks = {
        'DEBUG=True': 'DEBUG模式已启用',
        'QWEN_API_KEY=sk-': 'Qwen API密钥已配置',
    }
    
    all_passed = True
    for check, message in checks.items():
        if check in content:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ 缺少配置: {check}")
            all_passed = False
    
    return all_passed

def test_django_imports():
    """测试Django导入"""
    print("\n" + "=" * 60)
    print("测试2: 检查Django依赖")
    print("=" * 60)
    
    try:
        import django
        print(f"  ✅ Django {django.__version__}")
    except ImportError:
        print("  ❌ Django未安装")
        return False
    
    try:
        import rest_framework
        print(f"  ✅ Django REST Framework")
    except ImportError:
        print("  ❌ Django REST Framework未安装")
        return False
    
    try:
        import requests
        print(f"  ✅ Requests库")
    except ImportError:
        print("  ❌ Requests库未安装")
        return False
    
    return True

def test_api_key():
    """测试API密钥"""
    print("\n" + "=" * 60)
    print("测试3: 检查API密钥")
    print("=" * 60)
    
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    qwen_key = os.getenv('QWEN_API_KEY')
    if qwen_key and qwen_key.startswith('sk-'):
        print(f"  ✅ Qwen API密钥已配置: {qwen_key[:10]}...")
        return True
    else:
        print("  ❌ Qwen API密钥未正确配置")
        return False

def test_database():
    """测试数据库"""
    print("\n" + "=" * 60)
    print("测试4: 检查数据库")
    print("=" * 60)
    
    try:
        import django
        django.setup()
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        print("  ✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"  ❌ 数据库连接失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("\n🚀 智能对话系统 - 快速诊断工具")
    print("=" * 60)
    
    results = []
    
    # 测试1: .env文件
    results.append(("env配置", test_env_file()))
    
    # 测试2: Django依赖
    results.append(("Django依赖", test_django_imports()))
    
    # 测试3: API密钥
    try:
        results.append(("API密钥", test_api_key()))
    except Exception as e:
        print(f"  ❌ API密钥测试失败: {str(e)}")
        results.append(("API密钥", False))
    
    # 测试4: 数据库
    try:
        results.append(("数据库", test_database()))
    except Exception as e:
        print(f"  ❌ 数据库测试失败: {str(e)}")
        results.append(("数据库", False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！系统可以正常启动")
        print("\n启动命令:")
        print("  后端: python manage.py runserver 8080")
        print("  前端: cd ../frontend && npm run dev")
    else:
        print("❌ 部分测试失败，请先修复以上问题")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
