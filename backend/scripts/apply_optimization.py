import re

# 读取文件
with open('chatbot/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 stream_response_generator 函数并修改
old_code = '''        def stream_response_generator():
            full_response = ""
            try:
                # 立即返回一个初始消息，防止客户端超时
                yield f"data: {json.dumps({'content': ''})}" + "\\n\\n"
                
                # 在发送消息前，先检查知识库
                knowledge_context = ""
                try:
                    # 尝试从知识库中检索相关信息
                    from .utils.knowledge_base import knowledge_base_manager
                    if knowledge_base_manager.client is not None:
                        search_results = knowledge_base_manager.search(message_content, n_results=3)
                        if search_results and search_results.get('documents'):
                            # 将知识库检索结果整合为上下文
                            kb_docs = search_results['documents'][0]  # 取第一个结果的所有文档
                            if kb_docs:
                                knowledge_context = "基于知识库的相关信息：\\n" + "\\n".join(kb_docs[:2]) + "\\n\\n"
                except Exception as kb_error:
                    logger.warning(f"知识库检索失败：{str(kb_error)}")
                    # 知识库检索失败不影响主要功能，继续执行

                # 准备发送给 AI 的消息，包含知识库上下文
                enhanced_message = knowledge_context + message_content if knowledge_context else message_content'''

new_code = '''        def stream_response_generator():
            full_response = ""
            try:
                # 优化 1: 立即返回一个空格，让前端更快显示响应开始
                yield f"data: {json.dumps({'content': ' '})}" + "\\n\\n"
                
                # 优化 2: 尝试从缓存获取响应（快速路径）
                try:
                    cached_response = cache.get(cache_key)
                    if cached_response:
                        logger.info(f"✅ 使用缓存响应，节省 API 调用")
                        yield f"data: {json.dumps({'content': cached_response, 'from_cache': True})}" + "\\n\\n"
                        return
                except Exception as cache_error:
                    logger.warning(f"缓存不可用，跳过缓存：{cache_error}")
                
                # 优化 3: 在发送消息前，先检查知识库（带超时限制）
                knowledge_context = ""
                try:
                    # 设置 3 秒超时，避免知识库检索拖慢响应
                    old_timeout = socket.getdefaulttimeout()
                    socket.setdefaulttimeout(3)
                    
                    from .utils.knowledge_base import knowledge_base_manager
                    if knowledge_base_manager.client is not None:
                        # 减少检索数量从 3 到 2
                        search_results = knowledge_base_manager.search(message_content, n_results=2)
                        if search_results and search_results.get('documents'):
                            kb_docs = search_results['documents'][0]
                            if kb_docs:
                                # 只使用最相关的 1 条，减少上下文长度
                                knowledge_context = "\\n".join(kb_docs[:1]) + "\\n\\n"
                    
                    socket.setdefaulttimeout(old_timeout)
                except Exception as kb_error:
                    logger.warning(f"⚠️ 知识库检索超时或失败（已跳过）: {str(kb_error)}")
                    # 知识库检索失败不影响主要功能，继续执行

                # 准备发送给 AI 的消息，包含知识库上下文
                enhanced_message = knowledge_context + message_content if knowledge_context else message_content'''

# 替换
if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ 成功修改 stream_response_generator 函数")
else:
    print("❌ 未找到要替换的代码")
    print("正在尝试其他方式...")

# 保存文件
with open('chatbot/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("💾 文件已保存")
