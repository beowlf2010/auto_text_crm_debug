"""
 dashboard.tasks – Celery helpers for AI follow-ups, scoring and SMS, plus synchronous
 AI‑message builder.

 This module defines both the synchronous helper (``generate_ai_message``) used by
 views and the Celery tasks (``generate_ai_message_task``, ``send_ai_message_task``,
 ``queue_ai_followups_task``, etc.).
"""

from __future__ import annotations

import logging
import os
from datetime import timedelta, time

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from ..models import Lead, Message
from ..utils.ai import compose_outbound_text
from ..utils.sms import send_sms

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────────────────
# Config / constants
# ────────────────────────────────────────────────────────────────────────────────

SEND_WINDOW_START: time       = getattr(settings, "SEND_WINDOW_START", time(8, 0))
SEND_WINDOW_END:   time       = getattr(settings, "SEND_WINDOW_END",   time(20, 0))
FOLLOW_UP_COOLDOWN: timedelta = getattr(settings, "FOLLOW_UP_COOLDOWN", timedelta(days=2))

TWILIO_PHONE_NUMBER = (
    getattr(settings, "TWILIO_PHONE_NUMBER", None) or os.getenv("TWILIO_PHONE_NUMBER")
)
TWILIO_ACCOUNT_SID = (
    getattr(settings, "TWILIO_ACCOUNT_SID", None) or os.getenv("TWILIO_ACCOUNT_SID")
)
TWILIO_AUTH_TOKEN = (
    getattr(settings, "TWILIO_AUTH_TOKEN", None) or os.getenv("TWILIO_AUTH_TOKEN")
)

# ────────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ────────────────────────────────────────────────────────────────────────────────

def _best_phone(lead: Lead) -> str:
    """Return the first non-empty phone field for the lead, or an empty string."""
    return (lead.cellphone or lead.dayphone or lead.evephone or "").strip()


# ────────────────────────────────────────────────────────────────────────────────
# Synchronous helper – called from views for instant feedback
# ────────────────────────────────────────────────────────────────────────────────

def generate_ai_message(lead: Lead, prompt: str = "") -> str:
    """Build an outbound draft synchronously so the UI can show it immediately."""
    thread = list(
        Message.objects.filter(lead=lead)
        .order_by("-timestamp")[:10]
        .values("direction", "content")
    )
    draft = compose_outbound_text(prompt=prompt, thread=thread, lead=lead)
    return draft


# ────────────────────────────────────────────────────────────────────────────────
# Celery tasks
# ────────────────────────────────────────────────────────────────────────────────


@shared_task
def generate_ai_message_task(lead_id: int) -> None:
    """Generate a fresh AI draft and save it to ``Lead.ai_message``."""
    lead = Lead.objects.get(pk=lead_id)
    draft = generate_ai_message(lead)
    lead.ai_message = draft
    lead.save(update_fields=["ai_message"])
    logger.info("Draft generated for lead %s", lead.id)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_ai_message_task(self, lead_id: int) -> None:
    """Send the stored AI draft via Twilio and log the outbound."""
    lead = Lead.objects.get(pk=lead_id)

    if not lead.ai_message:
        logger.info("Lead %s – nothing to send", lead.id)
        return

    phone = _best_phone(lead)
    if not phone:
        logger.warning("Lead %s has no phone number – skipping send", lead.id)
        return

    try:
        sid = send_sms(
            to_number=phone,
            body=lead.ai_message,
            from_number=TWILIO_PHONE_NUMBER,
            account_sid=TWILIO_ACCOUNT_SID,
            auth_token=TWILIO_AUTH_TOKEN,
        )
    except Exception as exc:
        logger.error("SMS send failed for lead %s – %s", lead.id, exc)
        raise self.retry(exc=exc, countdown=30)

    Message.objects.create(
        lead=lead,
        content=lead.ai_message,
        direction=Message.Direction.OUTBOUND,
        source="AI",
        twilio_sid=sid,
        sent_by_ai=True,
        timestamp=timezone.now(),
    )
    lead.last_texted = timezone.now()
    lead.ai_message = ""
    lead.ai_message_count += 1
    lead.save(update_fields=["last_texted", "ai_message", "ai_message_count"])
    logger.info("SMS sent for lead %s (SID %s)", lead.id, sid)


@shared_task
def queue_ai_followups_task() -> None:
    """Beat-triggered scan that prepares/sends follow-ups (max 6 per run)."""
    now = timezone.now()
    start = now.replace(hour=SEND_WINDOW_START.hour, minute=0, second=0, microsecond=0)
    end   = now.replace(hour=SEND_WINDOW_END.hour,   minute=0, second=0, microsecond=0)

    if not (start <= now <= end):
        return

    leads = (
        Lead.objects
        .filter(last_texted__lt=now - FOLLOW_UP_COOLDOWN)
        .order_by("last_texted")[:6]
    )

    for lead in leads:
        if lead.ai_message:
            send_ai_message_task.delay(lead.id)
        else:
            generate_ai_message_task.delay(lead.id)

    logger.info("Queued %s ready messages", leads.count())


@shared_task
def score_leads() -> None:
    """Placeholder for nightly lead-scoring job (future work)."""
    logger.debug("score_leads placeholder executed – nothing to do (yet)")


@shared_task
def send_scheduled_ai_messages() -> None:
    """Legacy alias so any old beat entries keep working."""
    logger.debug("send_scheduled_ai_messages alias invoked")
    queue_ai_followups_task.delay()
