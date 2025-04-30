# dashboard/views_messages.py
"""
Message‑centered views that are *not* AI‑toggle specific.
AI start/pause/regenerate now live in `views_ai.py`.

Endpoints
---------
POST /api/send-message/       – manual outbound SMS
POST /api/twilio-webhook/     – inbound Twilio callback
"""

import json
import logging
import os
from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.rest import Client

from .models import Lead, MessageLog

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------
# Manual outbound SMS
# --------------------------------------------------------------------
@csrf_exempt
@require_POST
def send_message_view(request):
    """Send a handwritten SMS immediately via Twilio."""
    try:
        data = json.loads(request.body or "{}")
        body = data.get("message", "").strip()
        lead_id = data.get("lead_id")

        if not (body and lead_id):
            return JsonResponse(
                {"success": False, "error": "Missing body or lead_id"}, status=400
            )

        lead = Lead.objects.get(pk=lead_id)

        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
        )
        tw_msg = client.messages.create(
            body=body,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=lead.cellphone,
        )

        MessageLog.objects.create(
            lead=lead,
            content=body,
            direction="OUT",
            source="Manual",
            read=True,
            twilio_sid=tw_msg.sid,
            delivery_status="queued",
            timestamp=timezone.now(),
        )

        # keep UI list fresh
        lead.last_texted = timezone.now()
        lead.message_status = "Sent"
        lead.save(update_fields=["last_texted", "message_status"])

        return JsonResponse({"success": True, "sid": tw_msg.sid})
    except Exception as exc:  # pragma: no cover
        logger.exception("Manual send error: %s", exc)
        return JsonResponse({"success": False, "error": str(exc)}, status=500)


# --------------------------------------------------------------------
# Inbound webhook ‑ Twilio
# --------------------------------------------------------------------
@csrf_exempt
@require_POST
def twilio_webhook(request):
    """Record the inbound SMS, flag the lead as replied & pause AI."""
    from_number = request.POST.get("From", "").strip()
    body = request.POST.get("Body", "").strip()

    if not (from_number and body):
        return HttpResponse(status=400)

    # match by last 10 digits
    lead = Lead.objects.filter(cellphone__endswith=from_number[-10:]).first()
    if not lead:
        logger.warning("SMS from unknown number %s", from_number)
        return HttpResponse(status=204)

    # log the message
    MessageLog.objects.create(
        lead=lead,
        from_number=from_number,
        content=body,
        direction="IN",
        source="IN",
        read=False,
        timestamp=timezone.now(),
    )

    # update lead flags
    lead.new_message = True
    lead.has_replied = True
    lead.ai_active = False          # pause future AI
    lead.next_ai_send_at = None
    lead.follow_up_stage = "Replied"
    lead.last_reply = timezone.now()
    lead.save(
        update_fields=[
            "new_message",
            "has_replied",
            "ai_active",
            "next_ai_send_at",
            "follow_up_stage",
            "last_reply",
        ]
    )

    return HttpResponse(status=204)
