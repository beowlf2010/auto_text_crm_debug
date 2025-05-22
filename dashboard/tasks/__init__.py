# C:\Projects\auto_text_crm_dockerized_clean\dashboard\tasks\__init__.py
"""
Task package initializer.

• Keeps legacy aliases so old task names still work
• Imports sub-modules so Celery registers their @shared_task / @periodic_task
"""

from celery import shared_task

# ─── Legacy aliases (only the tasks that actually exist) ─────────
from .ai_tasks import (  # noqa: E402  – imported after celery setup
    generate_ai_message_task as _generate_ai_message_task,
    send_ai_message_task     as _send_ai_message_task,
)

@shared_task(name="dashboard.tasks.generate_ai_message_task", bind=True)
def legacy_generate(self, *args, **kwargs):
    return _generate_ai_message_task.apply(args=args, kwargs=kwargs)

@shared_task(name="dashboard.tasks.send_ai_message_task", bind=True)
def legacy_send(self, *args, **kwargs):
    return _send_ai_message_task.apply(args=args, kwargs=kwargs)

# ─── Import additional task modules so Celery sees them ──────────
from . import follow_up   # process_due_followups periodic task
from . import scoring     # score_leads periodic task
