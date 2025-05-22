# C:\Projects\auto_text_crm_dockerized_clean\AutoTextCRM\celery.py
import os, django
from celery import Celery
from django.conf import settings

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "AutoTextCRM.settings"),
)
django.setup()

app = Celery("AutoTextCRM")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = settings.TIME_ZONE
app.conf.enable_utc = False      # match TIME_ZONE (America/Chicago)

app.autodiscover_tasks()

# Optional: periodic beat schedule if you use Celery Beat from code
app.conf.beat_schedule = {
    "process-due-followups-every-5-min": {
        "task": "dashboard.tasks.follow_up.process_due_followups",
        "schedule": 300,  # seconds
    },
}
