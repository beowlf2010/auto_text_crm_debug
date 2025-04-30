"""
dashboard/urls.py
Central router for all Dashboard endpoints.

• AI toggle / draft actions now point at `views_ai`
• Added approve‑message & skip‑message endpoints
"""

from django.urls import path

from . import views                               # KPI, lead lists, etc.
from . import views_messages as vm                # send SMS, Twilio webhook
from . import views_ai as ai                      # AI start / pause / queue
from .views_schedule import get_next_schedule
from .views_api import update_lead, export_hot_leads
from dashboard.upload_leads_view import upload_leads_view


urlpatterns = [
    # ------------------------------------------------------------------
    # ROOT & STATIC PAGES
    # ------------------------------------------------------------------
    path("", views.dashboard_view, name="dashboard_home"),

    # ------------------------------------------------------------------
    # FILE UPLOAD  &  INBOUND TWILIO WEBHOOK
    # ------------------------------------------------------------------
    path("upload-leads/", upload_leads_view, name="upload_leads"),
    path("twilio-webhook/", vm.twilio_webhook, name="twilio_webhook"),

    # ------------------------------------------------------------------
    # LEADS CRUD / EXPORT
    # ------------------------------------------------------------------
    path("leads/", views.get_all_leads, name="all_leads"),
    path("leads/<int:lead_id>/", update_lead, name="update_lead"),
    path("leads/export-hot/", export_hot_leads, name="export_hot_leads"),

    # ------------------------------------------------------------------
    # INBOX / MESSAGE THREADS
    # ------------------------------------------------------------------
    path("send-message/", vm.send_message_view, name="send_message"),
    path("message-thread/<int:lead_id>/", views.get_message_thread, name="message_thread"),
    path("unread-messages/", views.get_unread_messages, name="unread_messages"),
    path("mark-messages-read/", views.mark_messages_read, name="mark_messages_read"),
    path("clear-new-message/<int:lead_id>/", views.clear_new_message, name="clear_new_message"),

    # ------------------------------------------------------------------
    # LIGHTNING‑FAST AI ACTIONS  ⚡️
    # ------------------------------------------------------------------
    path("start-ai/<int:lead_id>/",        ai.start_ai,        name="start_ai"),
    path("pause-ai/<int:lead_id>/",        ai.pause_ai,        name="pause_ai"),
    path("regenerate-message/<int:lead_id>/", ai.regenerate_message, name="regenerate_message"),
    path("approve-message/<int:lead_id>/", ai.approve_message, name="approve_message"),
    path("skip-message/<int:lead_id>/",    ai.skip_message,    name="skip_message"),

    # ------------------------------------------------------------------
    # KPI & SCHEDULING HELPERS
    # ------------------------------------------------------------------
    path("kpi-summary/",     views.get_ai_kpi_summary, name="kpi_summary"),
    path("schedule-next/<int:lead_id>/", get_next_schedule,    name="schedule_next"),
]
