from celery import Celery
from celery.schedules import crontab
import os
from django.conf import settings
from celery import shared_task

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_text_crm.settings")
app = Celery("auto_text_crm")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Define periodic task schedule
app.conf.beat_schedule = {
    "auto-generate-ai-messages-every-5-minutes": {
        "task": "dashboard.tasks.auto_generate_messages",
        "schedule": crontab(minute="*/5"),  # every 5 minutes
    },
}
