# C:\Projects\auto_text_crm_dockerized_clean\dashboard\tasks\send_scheduled_ai_messages.py
"""
Celery task: dispatch outbound AI follow‑up texts, then schedule the next one.

Workflow
────────
1. Pick every lead that is:
      • opted_in_for_ai == True
      • opted_out        == False
      • has_replied      == False
      • next_ai_send_at  is null OR <= now
2. If no ai_message exists (or message_status == "Not Started") generate one
   on‑the‑fly with OpenAI (simple prompt – tweak later).
3. Send the SMS via Twilio, capture SID + status.
4. Log the message in MessageLog.
5. Ask the scheduler service for the next send‑time / stage → update Lead.
"""

import os
import logging
from datetime import timedelta

import openai
from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from twilio.rest import Client

from dashboard.models import Lead, MessageLog
from dashboard.services.ai_scheduler import get_next_send

logger = logging.getLogger(__name__)

# Load secrets from env
openai.api_key = os.getenv("OPENAI_API_KEY")
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


@shared_task
def send_scheduled_ai_messages():
    now = timezone.now()

    leads = Lead.objects.filter(
        opted_in_for_ai=True,
        opted_out=False,
        has_replied=False
    ).filter(
        Q(next_ai_send_at__lte=now) | Q(next_ai_send_at__isnull=True)
    )

    sent_count = 0

    for lead in leads:
        try:
            # ------------------------------------------------------------------
            # 1. Generate message if missing / stale
            # ------------------------------------------------------------------
            if not lead.ai_message or lead.message_status == "Not Started":
                system_prompt = (
                    "You are an upbeat car sales rep. Draft a polite SMS in 300 "
                    "characters or fewer that references the lead’s first name, "
                    "vehicle of interest, and invites a reply."
                )
                user_context = (
                    f"Lead name: {lead.firstname} {lead.lastname}\n"
                    f"Vehicle: {lead.vehicle_interest or 'a new vehicle'}\n"
                    f"Source: {lead.source or 'website inquiry'}\n"
                )

                completion = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_context},
                    ],
                    max_tokens=100, temperature=0.7,
                )
                lead.ai_message = completion.choices[0].message.content.strip()
                lead.message_status = "Generated"
                lead.save(update_fields=["ai_message", "message_status"])

            # Skip if we still have no message (safety)
            if not lead.ai_message:
                logger.warning("Lead %s has no AI message after generation ‑ skipping", lead.id)
                continue

            # ------------------------------------------------------------------
            # 2. Send SMS via Twilio
            # ------------------------------------------------------------------
            sms = twilio_client.messages.create(
                body=lead.ai_message,
                from_=TWILIO_NUMBER,
                to=lead.cellphone
            )

            # ------------------------------------------------------------------
            # 3. Log message
            # ------------------------------------------------------------------
            MessageLog.objects.create(
                lead=lead,
                content=lead.ai_message,
                source="AI",
                from_number=TWILIO_NUMBER,
                direction="OUT",
                sent_by_ai=True,
                twilio_sid=sms.sid,
                delivery_status=sms.status,
                follow_up_stage=lead.follow_up_stage,
            )

            # ------------------------------------------------------------------
            # 4. Schedule next send
            # ------------------------------------------------------------------
            next_dt, next_stage = get_next_send(
                current_stage=lead.follow_up_stage,
                last_send_at=now,
                lead_created=lead.created_at,
            )

            lead.follow_up_stage = next_stage or lead.follow_up_stage
            lead.next_ai_send_at = next_dt
            lead.ai_message_count += 1
            lead.last_texted = now
            lead.message_status = "Sent"
            lead.save(update_fields=[
                "follow_up_stage",
                "next_ai_send_at",
                "ai_message_count",
                "last_texted",
                "message_status",
            ])

            sent_count += 1

        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to send AI message for lead %s: %s", lead.id, exc)

    return f"AI follow‑ups dispatched: {sent_count}"
