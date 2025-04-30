# C:\Projects\auto_text_crm_dockerized_clean\dashboard\services\lead_scoring.py
"""
Pure function: calculate_score(lead) → int  (0‑100)

Weighting (v1 — tweak anytime):
+25  if lead.opted_in_for_ai
+20  if lead.new_message            (unread customer reply)
+15  if lead.created < 3 days ago
+10  if lead.vehicle_interest
+10  if lead.message_status == "Generated"
"""
from datetime import timedelta
from django.utils import timezone


def calculate_score(lead) -> int:
    score = 0

    if lead.opted_in_for_ai:
        score += 25

    if lead.new_message:
        score += 20

    if lead.created_at and lead.created_at >= timezone.now() - timedelta(days=3):
        score += 15

    if lead.vehicle_interest:
        score += 10

    if lead.message_status == "Generated":
        score += 10

    return min(score, 100)
