# C:\Projects\auto_text_crm_dockerized_clean\auto_text_crm\urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Existing API routes (leads, Smart Inbox, KPI widgets, etc.)
    path("api/", include("dashboard.urls")),

    # NEW — Inbox‑specific API (Twilio webhook and any future inbox endpoints)
    # /api/twilio-webhook/  →  auto_text_crm.inbox.views.twilio_sms_webhook
    path("api/", include("auto_text_crm.inbox.urls")),
]
