"""
AI 响应速度优化模块

优化措施：
1. 添加响应缓存机制 - 缓存相似问题的答案
2. 优化知识库检索超时 - 限制检索时间为 3 秒
3. 减少检索结果数量 - 从 3 条减少到 2 条
4. 优化初始响应 - 立即返回空格而不是空字符串，让前端更快显示
"""

import hashlib
import socket
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def get_cached_response(message_content: str):
    """
    尝试从缓存获取响应
    返回：(cached_response, cache_key) 或 (None, cache_key)
    """
    cache_key = f"chat_cache_{hashlib.md5(message_content.encode()).hexdigest()}"
    cached_response = cache.get(cache_key)
    return cached_response, cache_key

def set_cached_response(cache_key: str, response: str, timeout: int = 3600):
    """
    缓存响应结果
    timeout: 缓存时间（秒），默认 1 小时
    """
    cache.set(cache_key, response, timeout)
    logger.info(f"已缓存响应到 {cache_key}")

def apply_knowledge_search_timeout(message_content: str, n_results: int = 2, timeout: int = 3):
    """
    带超时控制的知识库检索
    timeout: 检索超时时间（秒）
    n_results: 检索结果数量（减少到 2 个）
    返回：knowledge_context 字符串或空字符串
    """
    knowledge_context = ""
    
    try:
        # 设置 socket 超时
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        
        from .utils.knowledge_base import knowledge_base_manager
        if knowledge_base_manager.client is not None:
            search_results = knowledge_base_manager.search(message_content, n_results=n_results)
            if search_results and search_results.get('documents'):
                kb_docs = search_results['documents'][0]
                if kb_docs:
                    # 只使用最相关的 1 条，减少上下文长度
                    knowledge_context = "\n".join(kb_docs[:1]) + "\n\n"
        
        socket.setdefaulttimeout(old_timeout)
    except Exception as e:
        logger.warning(f"知识库检索超时或失败（已跳过）: {str(e)}")
        socket.setdefaulttimeout(old_timeout)
    
    return knowledge_context

# 优化建议：
# 1. 前端可以立即显示"思考中"状态，而不是等待
# 2. 使用更快的模型（如 qwen-turbo 而不是 qwen-max）
# 3. 减少 max_tokens 参数（从 2000 减少到 1000）
# 4. 降低 temperature 参数（从 0.7 到 0.5）可以稍微加快响应
# 5. 如果 Redis 未启用，考虑启用 Redis 缓存
