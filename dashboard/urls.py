# C:\Projects\auto_text_crm_dockerized_clean\dashboard\urls.py
from django.urls import path

from . import views                               # KPI, leads, AI actions
from . import views_messages as vm                # Twilio send / webhook
from .views_schedule import get_next_schedule     # scheduling helper
from .views_api import update_lead, export_hot_leads
from dashboard.upload_leads_view import upload_leads_view

urlpatterns = [
    # ─── ROOT / HEALTH ──────────────────────────────────────────
    path("", views.dashboard_view, name="dashboard_home"),

    # ─── FILE UPLOAD & TWILIO ──────────────────────────────────
    path("upload-leads/",   upload_leads_view,   name="upload_leads"),
    path("twilio-webhook/", vm.twilio_webhook,   name="twilio_webhook"),

    # ─── LEADS CRUD / EXPORT ───────────────────────────────────
    path("leads/",                    views.get_all_leads, name="all_leads"),
    path("leads/<int:lead_id>/",      update_lead,         name="update_lead"),
    path("leads/export-hot/",         export_hot_leads,    name="export_hot_leads"),

    # ─── INBOX / THREADS ───────────────────────────────────────
    path("send-message/",                   views.send_message,          name="send_message"),
    path("message-thread/<int:lead_id>/",   views.get_message_thread,    name="message_thread"),
    path("unread-messages/",                views.get_unread_messages,   name="unread_messages"),
    path("mark-messages-read/",             views.mark_messages_read,    name="mark_messages_read"),
    path("clear-new-message/<int:lead_id>/",views.clear_new_message,     name="clear_new_message"),

    # ─── AI ACTIONS ────────────────────────────────────────────
    path("regenerate-message/<int:lead_id>/", views.regenerate_ai_message, name="regenerate_message"),
    path("approve-message/<int:lead_id>/",    views.approve_message,       name="approve_message"),
    path("approve-send/<int:lead_id>/",       views.approve_and_send_now,  name="approve_send_now"),
    path("send-now/<int:lead_id>/",           views.send_ai_message_now,   name="send_now"),
    path("skip-message/<int:lead_id>/",       views.skip_message,          name="skip_message"),
    path("start-ai/<int:lead_id>/",           views.start_ai_followup,     name="start_ai"),
    path("pause-ai/<int:lead_id>/",           views.pause_ai_followup,     name="pause_ai"),
    path("toggle-ai/<int:lead_id>/",          views.toggle_ai_opt_in,      name="toggle_ai"),

    # ─── SETTINGS ──────────────────────────────────────────────
    path("settings/", views.settings_view, name="settings"),

    # ─── KPI & SCHEDULING HELPERS ──────────────────────────────
    path("kpi-summary/",              views.get_ai_kpi_summary,   name="kpi_summary"),
    path("schedule-next/<int:lead_id>/", get_next_schedule,       name="schedule_next"),
]
