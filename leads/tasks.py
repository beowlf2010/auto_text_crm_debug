# C:\Projects\auto_text_crm_dockerized_clean\leads\celery_tasks.py
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

# 🔄  POINT TO THE CANONICAL MODEL
from dashboard.models import Lead


@shared_task
def auto_generate_messages():
    """
    Every 5 min Celery Beat calls this task to auto‑create AI messages
    for newly‑opted‑in leads.  We now query dashboard.Lead, which has the
    full AI schema (message_status, score, etc.).
    """
    cutoff = timezone.now() - timedelta(hours=1)

    leads = Lead.objects.filter(
        message_status="Not Started",
        created_at__gte=cutoff,
        opted_in_for_ai=True,
    )[:50]  # safety batch

    for lead in leads:
        # ---- message generation stub (replace with real logic) ----
        lead.ai_message = f"Hi {lead.firstname or lead.name}, thanks for your interest!"
        lead.message_status = "Generated"
        lead.save(update_fields=["ai_message", "message_status"])

    return f"Generated {len(leads)} messages"
