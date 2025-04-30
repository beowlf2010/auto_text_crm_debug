# C:\Projects\auto_text_crm_dockerized_clean\dashboard\views_api.py
"""
REST‑style helpers (no DRF serializers to keep it lightweight).

Endpoints
─────────
GET    /api/leads/               – list leads  (add ?hot=true or ?min_score=70)
PATCH  /api/leads/<id>/          – partial update  (opt‑in, tags, etc.)
PUT    /api/leads/<id>/          – full update    (name, phones, etc.)
GET    /api/leads/export-hot/    – CSV of hot leads (score ≥ threshold)
"""

import csv
import io
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from dashboard.models import Lead


# ────────────────────────────────────────────────────────────────
#  LIST  /api/leads/?hot=true
# ────────────────────────────────────────────────────────────────
@require_http_methods(["GET"])
def get_all_leads(request):
    queryset = Lead.objects.all()

    hot_flag = request.GET.get("hot")
    min_score = int(request.GET.get("min_score", 80))
    if hot_flag in ("true", "1"):
        queryset = queryset.filter(score__gte=min_score)

    leads_json = [
        model_to_dict(
            lead,
            exclude=["extra_data", "messages"],  # keep payload lean
        )
        for lead in queryset
    ]
    return JsonResponse(leads_json, safe=False, status=200)


# ────────────────────────────────────────────────────────────────
#  UPDATE  /api/leads/<id>/
# ────────────────────────────────────────────────────────────────
@require_http_methods(["PATCH", "PUT"])
def update_lead(request, lead_id: int):
    lead = get_object_or_404(Lead, pk=lead_id)

    try:
        data = json.loads(request.body.decode())
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Simple safety: only allow certain fields via API
    allowed = {
        "opted_in_for_ai",
        "opted_out",
        "new_message",
        "ai_message",
        "message_status",
        "tags",
        "follow_up_stage",
        "next_ai_send_at",
        "name",
        "firstname",
        "lastname",
        "cellphone",
        "email",
        "vehicle_interest",
    }

    dirty = False
    for key, val in data.items():
        if key in allowed:
            setattr(lead, key, val)
            dirty = True

    if dirty:
        lead.save()
        return JsonResponse(model_to_dict(lead), status=200)

    return JsonResponse({"error": "No valid fields supplied"}, status=400)


# ────────────────────────────────────────────────────────────────
#  CSV EXPORT  /api/leads/export-hot/
# ────────────────────────────────────────────────────────────────
@require_http_methods(["GET"])
def export_hot_leads(request):
    min_score = int(request.GET.get("min_score", 80))

    hot_qs = Lead.objects.filter(score__gte=min_score).order_by("-score")
    if not hot_qs.exists():
        return JsonResponse({"error": "No hot leads found."}, status=404)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "name",
            "cellphone",
            "email",
            "vehicle_interest",
            "score",
            "created_at",
        ]
    )

    for lead in hot_qs:
        writer.writerow(
            [
                lead.id,
                lead.name,
                lead.cellphone,
                lead.email,
                lead.vehicle_interest,
                lead.score,
                lead.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="text/csv")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="hot_leads_score_{min_score}_plus.csv"'
    return response
