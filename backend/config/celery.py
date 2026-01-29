"""
Celery配置文件
"""
from celery import Celery
from celery.schedules import crontab
import os

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('chatbot')

# 使用配置前缀CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

# 配置定时任务
app.conf.beat_schedule = {
    # 每小时同步一次数据库内容到知识库
    'sync-knowledge-base-hourly': {
        'task': 'chatbot.tasks.sync_knowledge_base_from_db',
        'schedule': crontab(minute=0),  # 每小时执行
    },
    # 每天同步一次外部数据源
    'sync-external-data-daily': {
        'task': 'chatbot.tasks.sync_external_data_sources',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点执行
    },
}

app.conf.timezone = 'Asia/Shanghai'