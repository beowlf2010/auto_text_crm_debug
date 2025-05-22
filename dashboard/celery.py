# C:\Projects\auto_text_crm_dockerized_clean\dashboard\celery.py
"""
Celery application instance for the **dashboard** app.

2025-05-01  — Initial commit
-------------------------------------------------------------
* Creates a Celery app named “dashboard”
* Loads settings from `auto_text_crm.settings` (namespace `CELERY_…`)
* Auto-discovers tasks in **all** installed Django apps
* Registers the periodic schedule for `process_due_followups`
"""

from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# ---------------------------------------------------------------------------
# Environment / app bootstrap
# ---------------------------------------------------------------------------

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_text_crm.settings")

app = Celery("dashboard")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # finds tasks.py or tasks/ in each INSTALLED_APP

# ---------------------------------------------------------------------------
# Celery Beat – periodic schedules
# ---------------------------------------------------------------------------

app.conf.beat_schedule |= {
    # AI follow-up engine – every 5 minutes
    "dashboard.process_due_followups": {
        "task": "dashboard.tasks.follow_up.process_due_followups",
        "schedule": crontab(minute="*/5"),
        "options": {"queue": "ai_followups"},
    },
}

# Optional – let Django know Celery’s timezone (defaults to settings.TIME_ZONE)
app.conf.timezone = settings.TIME_ZONE

# Provide a shortcut for `celery -A dashboard.celery worker …`
__all__ = ("app",)
