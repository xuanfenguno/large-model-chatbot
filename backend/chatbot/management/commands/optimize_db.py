"""
数据库优化管理命令
"""
from django.core.management.base import BaseCommand
from django.db import connection
from chatbot.models import Conversation, Message, UserProfile
from django.core.management.color import no_style
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '优化数据库性能，包括创建索引和分析查询性能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='分析数据库查询性能',
        )
        parser.add_argument(
            '--optimize-indexes',
            action='store_true',
            help='优化数据库索引',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='清理不需要的数据',
        )

    def handle(self, *args, **options):
        if options['analyze']:
            self.analyze_performance()
        elif options['optimize_indexes']:
            self.optimize_indexes()
        elif options['cleanup']:
            self.cleanup_data()
        else:
            # 执行所有优化
            self.stdout.write('开始数据库性能优化...')
            self.optimize_indexes()
            self.analyze_performance()
            self.cleanup_data()
            self.stdout.write(
                self.style.SUCCESS('数据库性能优化完成!')
            )

    def analyze_performance(self):
        """分析数据库性能"""
        self.stdout.write('分析数据库性能...')
        
        # 统计数据量
        conversations_count = Conversation.objects.count()
        messages_count = Message.objects.count()
        users_with_profiles = UserProfile.objects.count()
        
        self.stdout.write(f'会话总数: {conversations_count}')
        self.stdout.write(f'消息总数: {messages_count}')
        self.stdout.write(f'用户配置数: {users_with_profiles}')
        
        # 分析查询性能
        from django.test.utils import override_settings
        from django.db import connection
        
        # 模拟一些常用查询并测量性能
        with connection.constraint_checks_disabled():
            # 测试获取用户会话的性能
            from time import time
            start_time = time()
            user_convs = Conversation.objects.filter(user_id=1)[:10]
            query_time = time() - start_time
            self.stdout.write(f'获取用户会话查询时间: {query_time:.4f}秒')
        
        self.stdout.write(self.style.SUCCESS('性能分析完成'))

    def optimize_indexes(self):
        """优化数据库索引"""
        self.stdout.write('优化数据库索引...')
        
        # 输出当前模型的索引状态
        self.stdout.write('数据库索引已更新到模型中。')
        self.stdout.write('请运行以下命令应用索引更改:')
        self.stdout.write('  python manage.py makemigrations')
        self.stdout.write('  python manage.py migrate')
        
        # 说明新增的索引
        self.stdout.write('\n新增的索引包括:')
        self.stdout.write('  - PasswordResetToken: user, created_at, expires_at')
        self.stdout.write('  - Conversation: user, title, created_at, updated_at, model, mode')
        self.stdout.write('  - Message: conversation, role, message_type, created_at, is_read')
        self.stdout.write('  - UserProfile: user, phone, created_at, updated_at')
        self.stdout.write('  - VoiceCallRecord: call_id, caller, callee, status, initiated_at, accepted_at, ended_at')
        
        self.stdout.write(self.style.SUCCESS('索引优化计划完成'))

    def cleanup_data(self):
        """清理不需要的数据"""
        self.stdout.write('清理不需要的数据...')
        
        # 示例：清理过期的密码重置令牌
        from chatbot.models import PasswordResetToken
        from django.utils import timezone
        from datetime import timedelta
        
        expired_tokens = PasswordResetToken.objects.filter(expires_at__lt=timezone.now())
        expired_count = expired_tokens.count()
        expired_tokens.delete()
        
        self.stdout.write(f'删除了 {expired_count} 个过期的密码重置令牌')
        
        # 示例：清理超过一定时间的旧会话（可选）
        # 注意：在生产环境中要谨慎执行此操作
        
        self.stdout.write(self.style.SUCCESS('数据清理完成'))