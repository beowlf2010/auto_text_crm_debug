# C:\Projects\auto_text_crm_dockerized_clean\auto_text_crm\inbox\views.py
"""
Webhook that captures every inbound SMS from Twilio, stores it in InboxMessage /
Message, and auto‑pauses AI follow‑ups when the customer replies “STOP”.
"""

import os
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from twilio.request_validator import RequestValidator

from dashboard.models import Lead, Message  # Lead + log live in dashboard app


# ------------------------------------------------------------------
# INBOUND SMS  ➜  http(s)://<domain>/api/twilio-webhook/
# ------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def twilio_sms_webhook(request):
    """
    • Validates Twilio signature (skipped if TWILIO_AUTH_TOKEN not set)
    • Looks up / creates the matching Lead
    • Saves the message as INCOMING, unread
    • Auto‑pauses AI follow‑up on any reply + handles STOP keywords
    • Returns bare <Response/> so Twilio is happy
    """
    # ── 1.  Validate request ───────────────────────────────────────
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if auth_token:  # optional in dev
        validator = RequestValidator(auth_token)
        signature = request.headers.get("X-Twilio-Signature", "")
        url = request.build_absolute_uri()
        if not validator.validate(url, request.POST, signature):
            return HttpResponseForbidden("Invalid Twilio signature")

    # ── 2.  Parse Twilio payload ───────────────────────────────────
    from_number = (request.POST.get("From") or "").strip()
    body        = (request.POST.get("Body") or "").strip()
    msid        = request.POST.get("MessageSid")

    # Strip +1, keep last 10 digits for matching
    normalized = from_number.replace("+", "").lstrip("1")[-10:]

    # ── 3.  Find/create Lead ───────────────────────────────────────
    lead = (
        Lead.objects.filter(cellphone__endswith=normalized).first()
        or Lead.objects.create(
            cellphone=normalized,
            name="Unknown",
            lead_source="SMS",  # adjust to your schema
        )
    )

    # ── 4.  Save in Message / InboxMessage ──────────────────────
    Message.objects.create(
        lead=lead,
        from_number=from_number,
        content=body,
        direction="IN",
        channel="SMS",
        delivery_status="Received",
        read=False,
        timestamp=timezone.now(),
    )

    # ── 5.  Auto‑pause AI + flag unread ────────────────────────────
    lead.has_replied = True
    lead.new_message = True
    lead.last_texted = timezone.now()

    # If customer wants to opt out, pause AI entirely
    if body.strip().upper() in {"STOP", "UNSUBSCRIBE", "STOPALL", "CANCEL", "END", "QUIT"}:
        lead.opted_in_for_ai = False

    # Pause current sequence whenever the customer replies
    if lead.opted_in_for_ai:
        lead.opted_in_for_ai = False

    lead.save(
        update_fields=[
            "has_replied",
            "new_message",
            "last_texted",
            "opted_in_for_ai",
        ]
    )

    # ── 6.  Respond to Twilio ──────────────────────────────────────
    # Empty <Response/> is enough; no auto‑reply.
    return HttpResponse("<Response></Response>", content_type="text/xml")
