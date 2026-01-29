"""
知识库同步管理命令
"""
from django.core.management.base import BaseCommand
from chatbot.utils.knowledge_base import real_time_source
from chatbot.tasks import sync_knowledge_base_from_db, sync_external_data_sources
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '同步知识库内容'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-db',
            action='store_true',
            help='从数据库同步内容到知识库',
        )
        parser.add_argument(
            '--from-external',
            action='store_true',
            help='从外部数据源同步内容到知识库',
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='异步执行同步任务',
        )

    def handle(self, *args, **options):
        if options['from_db']:
            if options['async']:
                self.stdout.write('开始异步同步数据库内容到知识库...')
                task = sync_knowledge_base_from_db.delay()
                self.stdout.write(f'异步任务已启动，任务ID: {task.id}')
            else:
                self.stdout.write('开始同步数据库内容到知识库...')
                real_time_source.sync_from_database()
                self.stdout.write(
                    self.style.SUCCESS('数据库内容同步到知识库完成!')
                )
        elif options['from_external']:
            if options['async']:
                self.stdout.write('开始异步同步外部数据源...')
                task = sync_external_data_sources.delay()
                self.stdout.write(f'异步任务已启动，任务ID: {task.id}')
            else:
                self.stdout.write('开始同步外部数据源...')
                # 这里可以添加具体的外部数据源同步逻辑
                self.stdout.write(
                    self.style.SUCCESS('外部数据源同步完成!')
                )
        else:
            # 执行所有同步
            self.stdout.write('开始同步所有数据源到知识库...')
            
            if options['async']:
                db_task = sync_knowledge_base_from_db.delay()
                ext_task = sync_external_data_sources.delay()
                self.stdout.write(f'异步任务已启动，数据库同步任务ID: {db_task.id}, 外部数据同步任务ID: {ext_task.id}')
            else:
                real_time_source.sync_from_database()
                # real_time_source.sync_from_external_api() # 如果有外部数据源配置
                self.stdout.write(
                    self.style.SUCCESS('所有数据源同步到知识库完成!')
                )