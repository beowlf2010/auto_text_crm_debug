from celery import shared_task
from dashboard.models import Lead, Message
from dashboard.utils.ai import compose_outbound_text
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_ai_message_task(lead_id: int):
    try:
        lead = Lead.objects.get(id=lead_id)
        thread = Message.objects.filter(lead=lead)  # no slicing here
        lead.ai_message = compose_outbound_text(prompt="", thread=thread, lead=lead)
        lead.ai_generated_at = timezone.now()
        lead.save()
        logger.info("Generated AI message for lead %s", lead.id)
    except Exception as e:
        logger.exception("Failed to generate AI message for lead %s: %s", lead_id, str(e))

@shared_task
def send_ai_message_task(lead_id: int):
    pass

@shared_task
def queue_ai_followups_task():
    pass
