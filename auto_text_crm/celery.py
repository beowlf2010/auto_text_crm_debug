# C:\Projects\auto_text_crm_dockerized_clean\dashboard\celery_tasks.py
"""
Celery application for the Auto-Text CRM.

Key additions
─────────────
• Explicit TIME_ZONE pick-up (for send-window math)
• Beat schedule “ai-follow-up-dispatch” – fires every 15 min and
  calls dashboard.queue_ai_followups_task
"""

from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# ────────────────────────────────────────────────────────────────────────────
#  Django settings & Celery app init
# ────────────────────────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_text_crm.settings")

app = Celery("dashboard")                     # name can match your app
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ────────────────────────────────────────────────────────────────────────────
#  Broker (Redis via Memurai on localhost)
# ────────────────────────────────────────────────────────────────────────────
app.conf.broker_url = "redis://localhost:6379/0"

# Make sure Celery knows the same local time as Django
app.conf.timezone = settings.TIME_ZONE
app.conf.enable_utc = False

# ────────────────────────────────────────────────────────────────────────────
#  Beat schedule – AI follow-up dispatcher
# ────────────────────────────────────────────────────────────────────────────
app.conf.beat_schedule = {
    "ai-follow-up-dispatch": {
        "task": "dashboard.queue_ai_followups_task",      # ← updated name
        "schedule": crontab(minute="*/15"),               # every 15 minutes
        "options": {"queue": "default"},
    },
}
