# File: dashboard/management/commands/create_autotext_schedule.py

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = 'Create or update scheduled task for auto_generate_messages'

    def handle(self, *args, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=15,
            period=IntervalSchedule.MINUTES,
        )

        task, created = PeriodicTask.objects.update_or_create(
            name='Auto Generate AI Messages',
            defaults={
                'interval': schedule,
                'task': 'dashboard.tasks.auto_generate_messages',
            }
        )

        self.stdout.write(self.style.SUCCESS(f"✅ Scheduled task set to run every 15 minutes."))
