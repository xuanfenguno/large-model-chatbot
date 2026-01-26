from django.core.management.base import BaseCommand
from ...middleware.rate_limit import clear_blacklisted_ips

class Command(BaseCommand):
    help = '清除IP黑名单中的所有IP地址'

    def handle(self, *args, **options):
        self.stdout.write('正在清除IP黑名单...')
        clear_blacklisted_ips()
        self.stdout.write(
            self.style.SUCCESS('成功清除IP黑名单和相关缓存记录！')
        )