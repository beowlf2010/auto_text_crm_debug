# C:\Projects\auto_text_crm_dockerized_clean\dashboard\tasks\score_leads.py
"""
Nightly task: refresh Lead.score for every active lead.
Runs via Celery Beat (see celery_tasks.py snippet below).
"""

from celery import shared_task
from django.db import transaction
from dashboard.models import Lead
from dashboard.services.lead_scoring import calculate_score


@shared_task
def score_all_leads():
    updated = 0

    with transaction.atomic():
        for lead in Lead.objects.all():
            new_score = calculate_score(lead)
            if lead.score != new_score:
                lead.score = new_score
                lead.save(update_fields=["score"])
                updated += 1

    return f"Lead scores refreshed: {updated} updated"
