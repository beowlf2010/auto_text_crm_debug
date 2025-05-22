"""
Django REST-style endpoints for the Auto-Text CRM backend.

Major sections
──────────────
• Root + settings
• Leads + Smart-Inbox helpers
• AI draft generation and follow-up controls
• KPI / badge helpers
"""
from __future__ import annotations

import json
from datetime import timedelta

from django.db.models import Avg, Case, F, When, Value, BooleanField
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)

from .models import Lead, Message
from .tasks.ai_tasks import (
    generate_ai_message_task as generate_ai_message,
    send_ai_message_task,
    queue_ai_followups_task,
)
from .utils.sms import send_sms


# ──────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────
def _coerce_payload(request):
    """
    Return a dict regardless of whether the client sent JSON or form-data.
    """
    try:                                        # 1) JSON?
        return json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        pass                                    # 2) fall back to POST
    return request.POST if request.POST else {}


# ─── Root / health ────────────────────────────────────────────
@require_GET
def dashboard_view(request):
    return HttpResponse("📊 Auto-Text CRM API root — backend healthy.")


# ─── Settings placeholder ─────────────────────────────────────
@csrf_exempt
@require_http_methods(["GET", "PUT"])
def settings_view(request):
    if request.method == "GET":
        return JsonResponse({"start_hour": 8, "end_hour": 19, "auto_followups": True})

    data = json.loads(request.body or "{}")
    return JsonResponse({"status": "ok", "received": data})


# ─── Leads list (queue page) ──────────────────────────────────
@require_GET
def get_all_leads(request):
    leads = Lead.objects.all()
    return JsonResponse({"leads": [l.to_dict() for l in leads]})


# ─── Smart-Inbox helpers ──────────────────────────────────────
@require_GET
def get_message_thread(request, lead_id: int):
    thread = (
        Message.objects
               .filter(lead_id=lead_id)
               .annotate(
                   from_customer=Case(
                       When(sent_by="customer", then=Value(True)),
                       default=Value(False),
                       output_field=BooleanField()
                   )
               )
               .values(
    "id",
    "timestamp",
    "sent_by",
    "from_customer",
    body_text=F("body"),
)
               .order_by("timestamp")
    )

    return JsonResponse({"messages": list(thread)}, safe=False)


# ─── Manual outbound SMS (send_message) ───────────────────────
@csrf_exempt
@require_POST
def send_message(request):
    payload = _coerce_payload(request)

    lead_id = payload.get("lead_id") or payload.get("id")
    body_text = (
        payload.get("message")
        or payload.get("content")
        or payload.get("body")
        or ""
    ).strip()

    if not lead_id or not body_text:
        return JsonResponse(
            {"error": "lead_id and message/content/body are required"}, status=400
        )

    lead = get_object_or_404(Lead, pk=lead_id)

    # Send the SMS
    try:
        to_number = lead.cellphone or lead.dayphone or lead.evephone
        if not to_number:
            return JsonResponse({"error": "No valid phone number found"}, status=400)
        send_sms(to_number, body_text)
    except Exception as exc:
        import traceback
        print("Twilio SEND ERROR:", traceback.format_exc())
        return JsonResponse({"error": f"gateway failure: {exc}"}, status=502)

    # Log the message
    Message.objects.create(
        lead=lead,
        body=body_text,
        direction=Message.Direction.OUTBOUND,
        source="Manual",
        read=True,
        timestamp=timezone.now(),
    )

    # Clear pending AI draft / timer
    lead.ai_message = ""
    lead.next_ai_send_at = None
    lead.last_texted = timezone.now()
    lead.new_message = False
    lead.save(
        update_fields=[
            "ai_message",
            "next_ai_send_at",
            "last_texted",
            "new_message",
        ]
    )

    queue_ai_followups_task.delay()
    return JsonResponse({"status": "ok"})


# ─── Draft regeneration & opt-in toggle ───────────────────────
@csrf_exempt
@require_POST
def regenerate_ai_message(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    generate_ai_message.delay(lead.id)
    lead.message_status = Lead.DraftStatus.PENDING
    lead.ai_draft_updated_at = timezone.now()
    lead.save(update_fields=["message_status", "ai_draft_updated_at"])
    return JsonResponse({"status": "queued"})


@csrf_exempt
@require_POST
def toggle_ai_opt_in(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.opted_in_for_ai = not lead.opted_in_for_ai
    lead.schedule_next_ai_send()
    return JsonResponse({"status": "ok", "opted_in": lead.opted_in_for_ai})


# ─── AI message queue actions ─────────────────────────────────
@csrf_exempt
@require_POST
def approve_message(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.message_status = Lead.DraftStatus.APPROVED
    lead.next_ai_send_at = timezone.now() + timedelta(minutes=5)
    lead.save(update_fields=["message_status", "next_ai_send_at"])
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_POST
def skip_message(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.message_status = Lead.DraftStatus.NOT_STARTED
    lead.next_ai_send_at = (lead.next_ai_send_at or timezone.now()) + timedelta(days=1)
    lead.save(update_fields=["message_status", "next_ai_send_at"])
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_POST
def approve_and_send_now(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    if lead.message_status != Lead.DraftStatus.APPROVED:
        lead.message_status = Lead.DraftStatus.APPROVED
        lead.save(update_fields=["message_status"])
    send_ai_message_task.delay(lead.id)
    return JsonResponse({"status": "queued"})


@csrf_exempt
@require_POST
def send_ai_message_now(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    if lead.message_status != Lead.DraftStatus.APPROVED:
        return JsonResponse({"error": "draft not approved"}, status=409)
    send_ai_message_task.delay(lead.id)
    return JsonResponse({"status": "queued"})


# ─── Message indicators for sidebar badge ─────────────────────
@require_GET
def get_unread_messages(request):
    messages = Message.objects.filter(sent_by="lead").order_by("-timestamp")[:20]
    data = [{"id": m.id, "body": m.body, "timestamp": m.timestamp} for m in messages]
    return JsonResponse(data, safe=False)


@require_POST
def mark_messages_read(request):
    Message.objects.filter(direction="IN", read=False).update(read=True)
    return JsonResponse({"status": "success"})


@require_POST
def clear_new_message(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.new_message = False
    lead.save(update_fields=["new_message"])
    return JsonResponse({"status": "cleared"})


# ─── KPI summary (dashboard card) ─────────────────────────────
@require_GET
def get_ai_kpi_summary(request):
    qs = Lead.objects.all()
    return JsonResponse({
        "hot_leads": qs.filter(score__gte=60).count(),
        "avg_score": round(qs.aggregate(avg=Avg("score"))["avg"] or 0, 2),
    })


# ─── Manual start / pause AI follow-ups ───────────────────────
@csrf_exempt
@require_POST
def start_ai_followup(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.opted_in_for_ai = True
    lead.ai_active = True
    lead.schedule_next_ai_send()
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_POST
def pause_ai_followup(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.ai_active = False
    lead.save(update_fields=["ai_active"])
    return JsonResponse({"status": "ok"})
