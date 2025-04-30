# C:\Projects\auto_text_crm_dockerized_clean\auto_text_crm\inbox\models.py
from django.db import models

# 🔄  Swap to the canonical Lead model
from dashboard.models import Lead          # <-- was  from leads.models import Lead


class InboxMessage(models.Model):
    """
    Simple inbox table so salespeople can see incoming + outgoing
    text/email in one place.
    """
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, related_name="inbox_messages"
    )
    direction = models.CharField(
        max_length=3, choices=[("IN", "Incoming"), ("OUT", "Outgoing")]
    )
    channel = models.CharField(
        max_length=10, choices=[("SMS", "SMS"), ("EMAIL", "Email")]
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.lead.name} [{self.direction}] {self.timestamp:%Y-%m-%d %H:%M}"
