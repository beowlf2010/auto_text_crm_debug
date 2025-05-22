# C:\Projects\auto_text_crm_dockerized_clean\dashboard\tasks\scoring.py
"""
Celery tasks for lead-scoring logic.

• ``score_single_lead`` – on-demand score refresh for one Lead (returns the new score)
• ``score_all_leads``   – bulk refresh, intended for Celery Beat
"""

import logging
from celery import shared_task
from django.utils import timezone as dj_tz
from dashboard.models import Lead

logger = logging.getLogger(__name__)


# ---------- Scoring algorithm helper ---------- #
def _calculate_score(lead: Lead) -> int:
    """
    Simple heuristic to rank leads 0–100.
    Tweak weights anytime – everything lives in one place.
    """
    score = 0

    # 1) How fresh is the lead?  (max 30 pts)
    hours_old = (dj_tz.now() - lead.created_at).total_seconds() / 3600
    if hours_old < 1:
        score += 30
    elif hours_old < 24:
        score += 20
    elif hours_old < 72:
        score += 10

    # 2) Unread replies bump urgency (25 pts)
    if getattr(lead, "unread_messages_count", 0):
        score += 25

    # 3) Next AI send is soon (≤6 h) (15 pts)
    if lead.next_ai_send_at:
        hours_to_next = (lead.next_ai_send_at - dj_tz.now()).total_seconds() / 3600
        if hours_to_next < 1:
            score += 15
        elif hours_to_next < 6:
            score += 10

    # 4) Lead source weighting (up to 15 pts)
    source_weights = {"Website": 15, "3rd-Party": 10, "Walk-In": 5}
    score += source_weights.get((lead.lead_source or "").title(), 0)

    # 5) High-demand vehicles (10 pts)
    hot_keywords = ("silverado", "corvette", "2500", "3500")
    if lead.vehicle_interest and any(k in lead.vehicle_interest.lower() for k in hot_keywords):
        score += 10

    return min(score, 100)  # keep it 0-100


# ---------- Celery tasks ---------- #
@shared_task(name="dashboard.tasks.score_single_lead")
def score_single_lead(lead_id: int) -> int:
    """
    Recalculate and persist score for **one** lead.
    Returns the new score (or 0 if the lead vanished).
    """
    try:
        lead = Lead.objects.get(id=lead_id)
    except Lead.DoesNotExist:
        logger.warning("Lead %s vanished before scoring.", lead_id)
        return 0

    new_score = _calculate_score(lead)
    Lead.objects.filter(id=lead_id).update(
        score=new_score,
        score_updated_at=dj_tz.now(),
    )
    logger.info("Scored lead %s → %s", lead_id, new_score)
    return new_score


@shared_task(name="dashboard.tasks.score_all_leads")
def score_all_leads() -> None:
    """
    Bulk-refresh **all** lead scores.
    Hook this to Celery Beat (e.g., every 15 min or hourly).
    """
    logger.info("Starting bulk lead-scoring run…")
    q = Lead.objects.all().only(
        "id",
        "created_at",
        "unread_messages_count",
        "next_ai_send_at",
        "lead_source",
        "vehicle_interest",
    )

    for lead in q.iterator():
        new_score = _calculate_score(lead)
        Lead.objects.filter(id=lead.id).update(
            score=new_score,
            score_updated_at=dj_tz.now(),
        )
    logger.info("Bulk lead-scoring complete.")
