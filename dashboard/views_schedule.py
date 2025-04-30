# File: C:\Users\beowl\OneDrive\Desktop\auto_text_crm_dockerized\dashboard\views_schedule.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dashboard.models import Lead
from datetime import timedelta
from django.utils.timezone import now

@csrf_exempt
def get_next_schedule(request, lead_id):
    try:
        lead = Lead.objects.get(pk=lead_id)
        if not lead.last_texted:
            return JsonResponse({
                "next": "Not scheduled",
                "stage": lead.follow_up_stage
            })

        stage = lead.follow_up_stage
        base = lead.last_texted

        # Define smart schedule logic
        next_time = None
        next_stage = None
        if stage == "Day 0":
            next_time = base + timedelta(hours=4)
            next_stage = "Day 1"
        elif stage == "Day 1":
            next_time = base + timedelta(days=1)
            next_stage = "Day 2"
        elif stage == "Day 2":
            next_time = base + timedelta(days=1)
            next_stage = "Day 3"
        elif stage == "Day 3":
            next_time = base + timedelta(days=4)
            next_stage = "Week 1"
        elif stage == "Week 1":
            next_time = base + timedelta(days=7)
            next_stage = "Week 2"
        elif stage == "Week 2":
            next_time = base + timedelta(days=14)
            next_stage = "Done"
        else:
            next_time = base + timedelta(days=3)
            next_stage = "Done"

        # Save updated follow-up stage
        lead.follow_up_stage = next_stage
        lead.save()

        # Reset follow-up stage to Day 0 if there's a reply
        if request.method == 'POST' and request.POST.get('reset') == 'true':
            lead.follow_up_stage = "Day 0"
            lead.save()

        return JsonResponse({
            "next": next_time.strftime("%Y-%m-%d %H:%M:%S"),
            "stage": next_stage
        })

    except Lead.DoesNotExist:
        return JsonResponse({"error": "Lead not found"}, status=404)
