from django.core.management.base import BaseCommand
from chatbot.middleware.rate_limit import BLACKLISTED_IPS

class Command(BaseCommand):
    help = 'Clear all IPs from the blacklist'

    def handle(self, *args, **options):
        count = len(BLACKLISTED_IPS)
        BLACKLISTED_IPS.clear()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleared {count} IPs from the blacklist')
        )