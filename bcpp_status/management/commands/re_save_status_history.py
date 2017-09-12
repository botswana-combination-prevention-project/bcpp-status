from datetime import datetime
from django.core.management.base import BaseCommand
from ...models import StatusHistory


class Command(BaseCommand):

    help = 'Re-Saving status history data for sync'

    def handle(self, *args, **options):

        status_history = StatusHistory.objects.filter(
            created__gt=datetime(2017, 9, 9))
        total_status_history = status_history.count()
        count = 0
        for status_history_dt in status_history:
            status_history_dt.save()
            count += 1
            self.stdout.write(self.style.SUCCESS(
                f'Succefully relaced {count} out of {total_status_history}.'))

        self.stdout.write(self.style.SUCCESS(
            f'Succefully Re-Saved {total_status_history} status history data records.'))
