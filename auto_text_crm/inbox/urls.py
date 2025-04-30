# C:\Projects\auto_text_crm_dockerized_clean\auto_text_crm\inbox\urls.py
from django.urls import path

from .views import (
    twilio_sms_webhook,
)

urlpatterns = [
    # POST from Twilio — captures every inbound SMS
    path("twilio-webhook/", twilio_sms_webhook, name="twilio_sms_webhook"),
]
