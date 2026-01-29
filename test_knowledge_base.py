"""
实时知识库功能测试脚本
"""
import os
import sys
import django
from django.conf import settings

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 配置Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chatbot.utils.knowledge_base import real_time_source

def test_knowledge_base():
    print("开始测试实时知识库功能...")
    
    # 测试添加文档
    print("\n1. 测试添加文档到知识库...")
    doc_id = "test_doc_1"
    content = "人工智能是计算机科学的一个分支，它试图理解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。"
    metadata = {"source": "test", "category": "AI"}
    
    try:
        real_time_source.add_document(doc_id, content, metadata)
        print(f"✓ 成功添加文档 {doc_id}")
    except Exception as e:
        print(f"✗ 添加文档失败: {e}")
        return
    
    # 测试搜索功能
    print("\n2. 测试知识库搜索功能...")
    try:
        results = real_time_source.search("什么是人工智能", n_results=1)
        if results:
            print(f"✓ 搜索成功，找到 {len(results)} 个结果")
            print(f"  内容: {results[0]['content'][:100]}...")
        else:
            print("✗ 搜索返回空结果")
    except Exception as e:
        print(f"✗ 搜索失败: {e}")
        return
    
    # 测试从数据库同步
    print("\n3. 测试从数据库同步数据...")
    try:
        real_time_source.sync_from_database()
        print("✓ 数据库同步成功")
    except Exception as e:
        print(f"✗ 数据库同步失败: {e}")
    
    # 测试获取相关上下文
    print("\n4. 测试获取相关上下文...")
    try:
        contexts = real_time_source.get_relevant_context("人工智能的定义是什么？")
        if contexts:
            print(f"✓ 获取到 {len(contexts)} 个相关上下文")
            print(f"  上下文: {contexts[0][:100]}...")
        else:
            print("✓ 获取上下文成功，但没有找到匹配的内容")
    except Exception as e:
        print(f"✗ 获取上下文失败: {e}")
    
    print("\n实时知识库功能测试完成！")

if __name__ == "__main__":
    test_knowledge_base()