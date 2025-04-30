# auto_text_crm_dockerized/leads/views.py

import csv
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Lead

@csrf_exempt
def upload_leads_view(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        created_count = 0
        updated_count = 0

        for row in reader:
            # Match CSV columns to your Lead model fields
            phone = row.get('phone', '').strip()
            name = row.get('name', '').strip()
            vehicle = row.get('vehicle', '').strip()
            lead_source = row.get('source', '').strip()  # rename as needed
            status = row.get('status', 'New').strip().title()  # e.g. "New"

            # If you added 'first_manual_sent' to Lead and want to import it:
            # first_manual = row.get('first_manual_sent', 'False').strip().lower() == 'true'

            if phone:
                lead, created_lead = Lead.objects.update_or_create(
                    phone=phone,
                    defaults={
                        'name': name,
                        'vehicle': vehicle,
                        'lead_source': lead_source,
                        'status': status,
                        # 'first_manual_sent': first_manual  # uncomment if using
                    }
                )

                if created_lead:
                    created_count += 1
                else:
                    updated_count += 1

        messages.success(request, f"{created_count} leads added, {updated_count} updated.")
        return redirect('dashboard')

    messages.error(request, "No file uploaded or wrong format.")
    return redirect('dashboard')
