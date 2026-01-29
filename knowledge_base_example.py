"""
实时知识库使用示例
注意：此示例演示了实时知识库的使用方法。
如果遇到网络连接问题，请确保网络畅通后再运行。
"""
import sys
import os
import django
from django.conf import settings

# 设置Django配置
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')

# 配置Django
django.setup()

from backend.chatbot.utils.knowledge_base import real_time_source

def example_usage():
    print("=== 实时知识库使用示例 ===\n")
    
    # 检查ChromaDB是否可用
    chromadb_available = getattr(real_time_source.kb_manager, 'collection', None) is not None
    
    if not chromadb_available:
        print("⚠️  ChromaDB 不可用，可能是因为:")
        print("   - 网络连接问题 (无法下载嵌入模型)")
        print("   - ChromaDB 服务未启动")
        print("   - 依赖包安装不完整")
        print("\n请确保满足以下条件:")
        print("   1. 网络连接正常")
        print("   2. 已安装所有依赖包 (pip install -r backend/requirements.txt)")
        print("   3. 如需持久化存储，确保 chromadb 服务可用")
        print("\n尽管如此，我们仍将演示API调用方法:\n")
    
    # 1. 添加文档到知识库
    print("1. 添加文档到知识库:")
    doc_id = "company_policy_2026"
    content = """
    公司政策更新 (2026年1月):
    - 工作时间: 早上9点至下午6点
    - 休息时间: 中午12点至1点
    - 加班政策: 超过晚上8点视为加班，享受加班费
    - 远程办公: 每周最多2天远程办公
    - 带薪休假: 每年15天带薪假期
    """
    
    try:
        real_time_source.add_document(
            doc_id=doc_id,
            content=content,
            metadata={
                "category": "company_policy",
                "year": 2026,
                "department": "HR"
            }
        )
        print(f"   ✓ 添加文档 {doc_id} 到知识库")
    except Exception as e:
        print(f"   ⚠️  添加文档失败: {e}")
    
    # 2. 搜索知识库
    print("\n2. 搜索知识库:")
    query = "公司加班政策是什么？"
    try:
        results = real_time_source.search(query, n_results=3)
        
        if results:
            print(f"   找到 {len(results)} 个相关结果:")
            for i, result in enumerate(results, 1):
                print(f"   结果 {i}: {result['content'][:100]}...")
                print(f"   距离: {result['distance']:.3f}")
        else:
            print("   未找到相关结果")
    except Exception as e:
        print(f"   ⚠️  搜索失败: {e}")
    
    # 3. 获取相关上下文
    print("\n3. 获取相关上下文:")
    try:
        contexts = real_time_source.get_relevant_context("员工工作时间安排", max_results=2)
        
        if contexts:
            print(f"   获取到 {len(contexts)} 个相关上下文:")
            for i, context in enumerate(contexts, 1):
                print(f"   上下文 {i}: {context[:100]}...")
        else:
            print("   未找到相关上下文")
    except Exception as e:
        print(f"   ⚠️  获取上下文失败: {e}")
    
    # 4. 从数据库同步数据
    print("\n4. 同步数据库数据到知识库:")
    try:
        real_time_source.sync_from_database()
        print("   ✓ 数据库数据已同步到知识库")
    except Exception as e:
        print(f"   ⚠️  同步数据库失败: {e}")
    
    # 5. 从外部API同步数据 (示例)
    print("\n5. 同步外部数据 (示例):")
    print("   示例: real_time_source.sync_from_external_api(api_endpoint, headers)")
    
    # 6. 从文件同步数据 (示例)
    print("\n6. 同步文件数据 (示例):")
    print("   示例: real_time_source.sync_from_files(file_paths)")
    
    print("\n💡 提示：要在实际项目中使用实时知识库，")
    print("   请确保在Django视图中调用 real_time_source 相关方法，")
    print("   系统会在用户提问时自动检索相关知识并增强AI回复。")

if __name__ == "__main__":
    example_usage()