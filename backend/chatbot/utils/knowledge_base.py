"""
实时知识库管理系统
"""
import os
from typing import List, Dict, Optional
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import logging
import uuid

logger = logging.getLogger(__name__)

CHROMADB_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    logger.warning("ChromaDB not available. Knowledge base functionality will be limited.")


class KnowledgeBaseManager:
    """
    实时知识库管理系统
    """
    def __init__(self, collection_name: str = "knowledge_base"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.embeddings = None
        self.text_splitter = None
        
        if CHROMADB_AVAILABLE:
            try:
                # 初始化向量数据库
                self.client = chromadb.PersistentClient(
                    path="./chroma_data",
                    settings=Settings(anonymized_telemetry=False)
                )
                
                # 创建或获取集合
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                
                # 初始化嵌入模型
                self.embeddings = SentenceTransformer('all-MiniLM-L6-v2')
                
                # 初始化文本分割器（简单的按长度分割）
                pass  # 我们将使用简单的字符串分割，不需要初始化text_splitter
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                # 不能在这里修改全局变量CHROMADB_AVAILABLE

    def _split_text(self, text: str) -> List[str]:
        """
        分割文本为块
        """
        # 简单的文本分割
        chunks = []
        chunk_size = 512
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def add_document(self, doc_id: str, content: str, metadata: Dict = None):
        """
        添加文档到知识库
        """
        if not CHROMADB_AVAILABLE or self.collection is None:
            logger.warning("ChromaDB not available, skipping document addition")
            return
        
        if metadata is None:
            metadata = {}
        
        # 分割文档
        chunks = self._split_text(content)
        
        # 为每个块生成嵌入
        embeddings = self.embeddings.encode(chunks).tolist()
        
        # 添加到向量数据库
        self.collection.add(
            documents=chunks,
            metadatas=[metadata for _ in chunks],
            ids=[f"{doc_id}_{i}" for i in range(len(chunks))],
            embeddings=embeddings
        )
        
        logger.info(f"Added document {doc_id} with {len(chunks)} chunks to knowledge base")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        搜索知识库
        """
        if not CHROMADB_AVAILABLE or self.collection is None:
            logger.warning("ChromaDB not available, skipping search")
            return []
        
        try:
            # 生成查询嵌入
            query_embedding = self.embeddings.encode([query]).tolist()[0]
            
            # 执行相似性搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # 格式化结果
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def update_document(self, doc_id: str, content: str, metadata: Dict = None):
        """
        更新文档
        """
        if not CHROMADB_AVAILABLE or self.collection is None:
            logger.warning("ChromaDB not available, skipping document update")
            return
        
        # 删除现有文档
        self.delete_document(doc_id)
        # 添加新文档
        self.add_document(doc_id, content, metadata)
    
    def delete_document(self, doc_id: str):
        """
        删除文档
        """
        if not CHROMADB_AVAILABLE or self.collection is None:
            logger.warning("ChromaDB not available, skipping document deletion")
            return
        
        # 获取匹配的文档ID
        try:
            all_docs = self.collection.get()
            ids_to_delete = [doc_id for doc_id in all_docs['ids'] if doc_id.startswith(f"{doc_id}_")]
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted document {doc_id} from knowledge base")
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
    
    def refresh_cache(self):
        """
        刷新缓存
        """
        cache.delete("knowledge_base_summary")
        logger.info("Knowledge base cache refreshed")


# 实时数据源处理器
class RealTimeDataSource:
    """
    实时数据源处理器
    """
    def __init__(self):
        self.kb_manager = KnowledgeBaseManager()
    
    def sync_from_database(self):
        """
        从数据库同步数据到知识库
        """
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available, skipping database sync")
            return
        
        from chatbot.models import Conversation, Message, UserProfile
        
        try:
            # 同步用户配置信息
            profiles = UserProfile.objects.all()
            for profile in profiles:
                doc_content = f"用户配置信息:\n" \
                             f"用户: {profile.user.username}\n" \
                             f"电话: {profile.phone or '未设置'}\n" \
                             f"API密钥配置: OpenAI={bool(profile.openai_api_key)}, " \
                             f"Qwen={bool(profile.qwen_api_key)}, " \
                             f"Gemini={bool(profile.gemini_api_key)}\n" \
                             f"更新时间: {profile.updated_at}\n"
                
                self.kb_manager.add_document(
                    doc_id=f"profile_{profile.user.id}",
                    content=doc_content,
                    metadata={
                        "type": "user_profile",
                        "user_id": profile.user.id,
                        "username": profile.user.username
                    }
                )
            
            # 同步会话信息
            conversations = Conversation.objects.all()
            for conv in conversations:
                doc_content = f"会话信息:\n" \
                             f"标题: {conv.title}\n" \
                             f"用户: {conv.user.username}\n" \
                             f"模型: {conv.model}\n" \
                             f"模式: {conv.mode}\n" \
                             f"创建时间: {conv.created_at}\n" \
                             f"更新时间: {conv.updated_at}\n"
                
                self.kb_manager.add_document(
                    doc_id=f"conversation_{conv.id}",
                    content=doc_content,
                    metadata={
                        "type": "conversation",
                        "user_id": conv.user.id,
                        "conversation_id": conv.id,
                        "model": conv.model
                    }
                )
            
            # 同步最近的消息内容（限制数量避免过多数据）
            recent_messages = Message.objects.order_by('-created_at')[:500]  # 限制数量
            for msg in recent_messages:
                doc_content = f"消息内容:\n" \
                             f"会话: {msg.conversation.title}\n" \
                             f"角色: {msg.role}\n" \
                             f"内容: {msg.content[:200]}...\n" \
                             f"时间: {msg.created_at}\n" \
                             f"类型: {msg.message_type}\n"
                
                self.kb_manager.add_document(
                    doc_id=f"message_{msg.id}",
                    content=doc_content,
                    metadata={
                        "type": "message",
                        "conversation_id": msg.conversation.id,
                        "role": msg.role,
                        "user_id": msg.conversation.user.id
                    }
                )
            
            logger.info(f"Synchronized {profiles.count()} profiles, {conversations.count()} conversations, and {recent_messages.count()} messages to knowledge base")
        except Exception as e:
            logger.error(f"Error syncing from database: {e}")
    
    def sync_from_external_api(self, api_endpoint: str, headers: dict = None):
        """
        从外部API同步数据
        """
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available, skipping external API sync")
            return
        
        import requests
        import json
        
        try:
            response = requests.get(api_endpoint, headers=headers or {})
            if response.status_code == 200:
                data = response.json()
                
                # 将API数据转换为知识库格式
                doc_content = f"外部API数据:\n" \
                             f"端点: {api_endpoint}\n" \
                             f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}\n" \
                             f"同步时间: {timezone.now()}\n"
                
                self.kb_manager.add_document(
                    doc_id=f"api_data_{str(uuid.uuid4())[:8]}",
                    content=doc_content,
                    metadata={
                        "type": "external_api",
                        "source": api_endpoint,
                        "sync_time": str(timezone.now())
                    }
                )
                
                logger.info(f"Synchronized data from external API: {api_endpoint}")
        except Exception as e:
            logger.error(f"Error syncing from external API {api_endpoint}: {e}")
    
    def sync_from_files(self, file_paths: List[str]):
        """
        从文件同步数据
        """
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available, skipping file sync")
            return
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc_content = f"文件内容 ({file_path}):\n{content[:1000]}..."  # 限制内容长度
                    
                    self.kb_manager.add_document(
                        doc_id=f"file_{os.path.basename(file_path)}_{str(uuid.uuid4())[:8]}",
                        content=doc_content,
                        metadata={
                            "type": "file",
                            "file_path": file_path,
                            "sync_time": str(timezone.now()),
                            "size": len(content)
                        }
                    )
                    
                    logger.info(f"Synchronized file to knowledge base: {file_path}")
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
    
    def add_document(self, doc_id: str, content: str, metadata: Dict = None):
        """
        添加文档到知识库
        """
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available, skipping document addition")
            return
        
        self.kb_manager.add_document(doc_id, content, metadata)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        搜索知识库
        """
        if not CHROMADB_AVAILABLE:
            return []
        
        return self.kb_manager.search(query, n_results=n_results)
    
    def get_relevant_context(self, query: str, max_results: int = 5) -> List[str]:
        """
        获取与查询相关的上下文
        """
        if not CHROMADB_AVAILABLE:
            return []
        
        results = self.kb_manager.search(query, n_results=max_results)
        return [result['content'] for result in results]


# 全局实例
knowledge_base_manager = KnowledgeBaseManager()
real_time_source = RealTimeDataSource()