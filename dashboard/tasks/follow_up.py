# C:\Projects\auto_text_crm_dockerized_clean\dashboard\tasks\follow_up.py
import logging, datetime
from django.db import transaction
from django.utils import timezone
from celery import shared_task
from .sms import send_sms  # your Twilio helper
from ..models import Lead
from ..utils.ai import generate_followup

logger = logging.getLogger(__name__)

@shared_task
def process_due_followups():
    """
    Every 5 min: find leads whose next_ai_send_at <= now, generate (or send) msg.
    """
    now = timezone.now()
    leads = (
        Lead.objects
        .select_for_update(skip_locked=True)
        .filter(next_ai_send_at__lte=now, status=Lead.Status.OPEN)
    )

    with transaction.atomic():
        for lead in leads:
            try:
                if lead.message_status == Lead.DraftStatus.DRAFT:
                    # Need a draft – generate AI
                    prompt = f"Follow-up for {lead.first_name} about {lead.vehicle}."
                    msg = generate_followup(prompt)
                    if msg:
                        lead.ai_draft = msg
                        lead.message_status = Lead.DraftStatus.APPROVED   # auto-approve
                        lead.ai_draft_updated_at = now
                        lead.save(update_fields=["ai_draft", "message_status", "ai_draft_updated_at"])
                elif lead.message_status == Lead.DraftStatus.APPROVED:
                    # Send the approved msg
                    send_sms(lead.phone, lead.ai_draft)
                    lead.mark_ai_message_sent(now)
            except Exception:
                logger.exception("Failed follow-up for lead %s", lead.pk)
