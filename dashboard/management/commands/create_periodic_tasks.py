# File: dashboard/management/commands/create_periodic_tasks.py

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

class Command(BaseCommand):
    help = "Create periodic task for auto-generating AI messages"

    def handle(self, *args, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=10,  # Every 10 minutes
            period=IntervalSchedule.MINUTES,
        )

        PeriodicTask.objects.update_or_create(
            name='Auto Generate AI Messages',
            defaults={
                'interval': schedule,
                'task': 'dashboard.tasks.auto_generate_messages',
                'args': json.dumps([]),
            },
        )

        self.stdout.write(self.style.SUCCESS("✅ Scheduled task created or updated."))
