"""
Celery application bootstrap for Auto-Text CRM.

Adds two periodic tasks via Celery Beat:
 • ai-follow-up-dispatch – every 15 min → dashboard.tasks.queue_ai_followups_task
 • lead-score-refresh     – nightly at 02:00 → dashboard.tasks.score_leads
"""

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# ────────────────────────────────────────────────────────────────────────────
# Django settings & Celery init
# ────────────────────────────────────────────────────────────────────────────

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_text_crm.settings")
app = Celery("dashboard")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # finds @shared_task in dashboard/tasks

# ────────────────────────────────────────────────────────────────────────────
# Broker (Redis)
# ────────────────────────────────────────────────────────────────────────────

app.conf.broker_url = "redis://localhost:6379/0"
app.conf.timezone   = settings.TIME_ZONE
app.conf.enable_utc = False

# ────────────────────────────────────────────────────────────────────────────
# Beat schedule
# ────────────────────────────────────────────────────────────────────────────

app.conf.beat_schedule = {
    "ai-follow-up-dispatch": {
        "task": "dashboard.tasks.queue_ai_followups_task",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": "default"},
    },
    "lead-score-refresh": {
        "task": "dashboard.tasks.score_leads",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "default"},
    },
}
