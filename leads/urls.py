from django.urls import path
from . import views
from .views import upload_leads_view

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('send-message/<int:lead_id>/', views.send_message, name='send_message'),
    path('send-bulk/', views.send_bulk_messages, name='send_bulk_messages'),
    path('run-followups/', views.run_followups, name='run_followups'),
    path('twilio-webhook/', views.twilio_webhook, name='twilio_webhook'),
    path('upload-leads/', upload_leads_view, name='upload_leads'),
]
