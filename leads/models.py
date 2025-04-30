from django.db import models


class Lead(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    vehicle = models.CharField(max_length=100, blank=True, null=True)
    lead_source = models.CharField(max_length=100, blank=True, null=True)

    # If you'd like to keep a simple "status" with a default of "New"
    status = models.CharField(max_length=50, default="New")

    # Track when the lead was created
    created_at = models.DateTimeField(auto_now_add=True)

    # NEW FIELD: Indicate if the first manual message has been sent
    # This ensures your AI follow-ups only start AFTER you manually text the lead once
    first_manual_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    @property
    def score(self):
        """
        Optional scoring logic based on message count.
        Works if Message model has related_name='messages'.
        """
        msg_count = self.messages.count()
        if msg_count >= 3:
            return "HOT"
        elif msg_count == 2:
            return "WARM"
        return "COLD"
