# File: C:\Projects\auto_text_crm_dockerized_clean\dashboard\views_ai.py
# 🆕 2025-04-23 — Approve endpoint now bumps next_ai_send_at + sets opted_in_for_ai
"""Endpoints that toggle AI, regenerate drafts, approve/skip messages.
All kept lightweight for snappy React UX.
"""

from datetime import timedelta

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Lead
from .views_schedule import get_next_schedule
from .tasks import (
    generate_ai_message,
    generate_ai_message_task,
    send_ai_message_task,
)

# ---------------------------------------------------------------------------
#  QUICK TOGGLES
# ---------------------------------------------------------------------------

@require_POST
def start_ai(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    lead.ai_active = True
    first_send = get_next_schedule(lead)
    lead.next_ai_send_at = first_send
    lead.save(update_fields=["ai_active", "next_ai_send_at"])
    return JsonResponse({"success": True, "next_send": first_send.isoformat() if first_send else None})

@require_POST
def pause_ai(request, lead_id):
    Lead.objects.filter(pk=lead_id).update(ai_active=False)
    return JsonResponse({"success": True})

# ---------------------------------------------------------------------------
#  REGENERATE MESSAGE
# ---------------------------------------------------------------------------

@require_POST
def regenerate_message(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    if not lead.opted_in_for_ai or lead.opted_out:
        return HttpResponseBadRequest("AI messaging not allowed for this lead.")

    # Lightweight instant response
    draft = generate_ai_message(lead)

    # Full async rebuild (logs + next steps)
    generate_ai_message_task.delay(lead_id)

    return JsonResponse({"success": True, "message": draft})

# ---------------------------------------------------------------------------
#  APPROVE / SKIP
# ---------------------------------------------------------------------------

@require_POST
def approve_message(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)

    if not lead.ai_message:
        return HttpResponseBadRequest("No draft available.")

    # mark approved & opt-in
    lead.message_status = "Approved"
    lead.opted_in_for_ai = True
    lead.ai_active = True

    # bump schedule if it is missing or already overdue
    if not lead.next_ai_send_at or lead.next_ai_send_at < timezone.now():
        lead.next_ai_send_at = timezone.now() + timedelta(minutes=5)

    lead.save(update_fields=[
        "message_status",
        "opted_in_for_ai",
        "ai_active",
        "next_ai_send_at",
    ])

    return JsonResponse({"success": True, "next_send": lead.next_ai_send_at.isoformat()} )

@require_POST
def skip_message(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    if not lead.ai_message:
        return HttpResponseBadRequest("No draft to skip.")

    lead.message_status = "Skipped"
    lead.ai_message = ""
    # push follow-up by 1 day
    lead.next_ai_send_at = timezone.now() + timedelta(days=1)
    lead.save(update_fields=["message_status", "ai_message", "next_ai_send_at"])
    return JsonResponse({"success": True})