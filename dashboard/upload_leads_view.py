import csv
import re
from dateutil.parser import parse as dateparse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from dashboard.models import Lead

@csrf_exempt
def upload_leads_view(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        created_count = 0
        updated_count = 0
        failed = 0

        for i, row in enumerate(reader, start=2):
            if not row or not row.get("cellphone"):
                continue

            phone = row.get("cellphone", "").strip()
            if not phone:
                failed += 1
                continue

            lead_data = {}
            extra_data = {}

            for field, value in row.items():
                val = value.strip()
                if hasattr(Lead, field):
                    lead_data[field] = val
                else:
                    extra_data[field] = val

            # 🚗 Vehicle detection
            year = row.get("VehicleYear", "").strip()
            make = row.get("VehicleMake", "").strip()
            model = row.get("VehicleModel", "").strip()
            if make or model:
                lead_data["vehicle_interest"] = f"{year} {make} {model}".strip()

            # 📅 Appointment detection
            for key, value in {**row, **extra_data}.items():
                try:
                    if isinstance(value, str) and re.search(r"\d{4}", value):
                        dt = dateparse(value, fuzzy=True)
                        extra_data["appointment_time"] = str(dt)
                        break
                except:
                    continue

            lead_data["extra_data"] = extra_data  # 💡 final dict injection

            try:
                lead, created = Lead.objects.update_or_create(
                    cellphone=phone,
                    defaults=lead_data
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                return HttpResponse(f"❌ ERROR on row {i}: {str(e)}", status=500)

        messages.success(request, f"✅ {created_count} created, {updated_count} updated, {failed} failed.")
        return redirect("dashboard-home")

    return HttpResponse("❌ No CSV file received.", status=400)
