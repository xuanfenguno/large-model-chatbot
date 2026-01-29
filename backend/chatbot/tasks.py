"""
知识库同步任务
"""
from celery import shared_task
from chatbot.utils.knowledge_base import real_time_source
import logging

logger = logging.getLogger(__name__)

@shared_task
def sync_knowledge_base_from_db():
    """
    定时同步数据库内容到知识库
    """
    try:
        logger.info("开始同步数据库内容到知识库...")
        real_time_source.sync_from_database()
        logger.info("数据库内容同步到知识库完成")
    except Exception as e:
        logger.error(f"同步数据库内容到知识库失败: {e}")

@shared_task
def sync_external_data_sources():
    """
    同步外部数据源
    """
    try:
        logger.info("开始同步外部数据源...")
        # 这里可以配置外部API端点
        external_sources = [
            # {
            #     'url': 'https://api.example.com/data',
            #     'headers': {'Authorization': 'Bearer YOUR_TOKEN'}
            # }
        ]
        
        for source in external_sources:
            real_time_source.sync_from_external_api(
                source['url'],
                source.get('headers', {})
            )
        
        logger.info("外部数据源同步完成")
    except Exception as e:
        logger.error(f"同步外部数据源失败: {e}")