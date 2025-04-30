# File: C:\Projects\auto_text_crm_dockerized_clean\dashboard\views.py
"""Core API endpoints for leads, Smart Inbox, and AI follow-up controls."""
from datetime import timedelta
import json

from django.db.models import Avg, F, Case, When, Value, BooleanField
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from openai import OpenAIError

from .models import Lead, MessageLog
from .tasks import generate_ai_message_task  # updated import

# ------------------------------------------------------------------
# DASHBOARD LANDING
# ------------------------------------------------------------------
@require_GET
def dashboard_view(request):
    return HttpResponse("📊 Django backend is running at /api/ — no template needed.")

# ------------------------------------------------------------------
# LEADS LIST
# ------------------------------------------------------------------
@require_http_methods(["GET"])
def get_all_leads(request):
    leads = Lead.objects.all()
    return JsonResponse({"leads": [l.to_dict() for l in leads]})

# ------------------------------------------------------------------
# MESSAGE THREAD (Smart Inbox right-pane)
# ------------------------------------------------------------------
@require_http_methods(["GET"])
def get_message_thread(request, lead_id: int):
    messages = (
        MessageLog.objects.filter(lead_id=lead_id)
        .order_by("timestamp")
        .values(
            "timestamp",
            "delivery_status",
            from_customer=Case(
                When(direction="IN", then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            body=F("content"),
        )
    )
    return JsonResponse({"messages": list(messages)})

# ------------------------------------------------------------------
# MANUAL OUTBOUND SMS
# ------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    data = json.loads(request.body)
    lead = get_object_or_404(Lead, id=data.get("lead_id"))
    body = data.get("message", "").strip()

    MessageLog.objects.create(
        lead=lead,
        content=body,
        direction="OUT",
        read=True,
        timestamp=timezone.now(),
    )

    lead.last_texted = timezone.now()
    lead.new_message = False
    lead.has_replied = True
    lead.save(update_fields=["last_texted", "new_message", "has_replied"])

    return JsonResponse({"status": "ok"})

# ------------------------------------------------------------------
# AI CONTROLS
# ------------------------------------------------------------------
@csrf_exempt
@require_POST
def regenerate_ai_message(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    try:
        draft = generate_ai_message(lead)
        lead.ai_message = draft
        lead.message_status = "Generated"
        lead.save(update_fields=["ai_message", "message_status"])
        return JsonResponse({"status": "ok", "message": draft})
    except OpenAIError as exc:
        return JsonResponse({"status": "error", "msg": str(exc)}, status=500)

@csrf_exempt
@require_POST
def toggle_ai_opt_in(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.opted_in_for_ai = not lead.opted_in_for_ai
    lead.save(update_fields=["opted_in_for_ai"])
    return JsonResponse({"status": "ok", "opted_in": lead.opted_in_for_ai})

# ------------------------------------------------------------------
# UNREAD MESSAGE FEED (Leads left-pane badge / toast)
# ------------------------------------------------------------------
@require_GET
def get_unread_messages(request):
    rows = (
        MessageLog.objects.filter(direction="IN", read=False)
        .order_by("-timestamp")[:20]
        .values(
            "from_number",
            "timestamp",
            lead_name=F("lead__name"),
            message=F("content"),
        )
    )
    return JsonResponse({"messages": list(rows)})

@require_POST
def mark_messages_read(request):
    MessageLog.objects.filter(direction="IN", read=False).update(read=True)
    return JsonResponse({"status": "success"})

@require_POST
def clear_new_message(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.new_message = False
    lead.save(update_fields=["new_message"])
    return JsonResponse({"status": "cleared"})

# ------------------------------------------------------------------
# KPI SUMMARY (dashboard widget)
# ------------------------------------------------------------------
@require_GET
def get_ai_kpi_summary(request):
    qs = Lead.objects.all()
    return JsonResponse({
        "hot_leads": qs.filter(score__gte=60).count(),
        "avg_score": round(qs.aggregate(avg=Avg("score"))["avg"] or 0, 2),
    })

# ------------------------------------------------------------------
# QUICK AI START / PAUSE
# ------------------------------------------------------------------
@csrf_exempt
@require_POST
def start_ai_followup(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.opted_in_for_ai = True
    lead.next_ai_send_at = timezone.now() + timedelta(minutes=5)
    lead.save(update_fields=["opted_in_for_ai", "next_ai_send_at"])
    return JsonResponse({"status": "ok"})

@csrf_exempt
@require_POST
def pause_ai_followup(request, lead_id: int):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.opted_in_for_ai = False
    lead.save(update_fields=["opted_in_for_ai"])
    return JsonResponse({"status": "ok"})