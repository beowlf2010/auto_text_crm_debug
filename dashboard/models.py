# ✅ LOCKED: 2025-04-23 — Models verified working with AI messaging, regenerate prompt, and Celery task system.

from django.db import models


class Lead(models.Model):
    """Represents a single lead / prospect in the system."""

    # ------------------------------------------------------------------
    # Basic Contact Info
    # ------------------------------------------------------------------
    firstname   = models.CharField(max_length=100, blank=True)
    middlename  = models.CharField(max_length=100, blank=True)
    lastname    = models.CharField(max_length=100, blank=True)
    name        = models.CharField(max_length=255, blank=True)
    email       = models.EmailField(blank=True)
    emailalt    = models.EmailField(blank=True)
    dayphone    = models.CharField(max_length=20, blank=True)
    evephone    = models.CharField(max_length=20, blank=True)
    cellphone   = models.CharField(max_length=20, unique=True)

    # ------------------------------------------------------------------
    # Address Info
    # ------------------------------------------------------------------
    address     = models.CharField(max_length=255, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    state       = models.CharField(max_length=100, blank=True)
    postalcode  = models.CharField(max_length=20, blank=True)

    # ------------------------------------------------------------------
    # Vehicle Info
    # ------------------------------------------------------------------
    vehicle_interest     = models.CharField(max_length=255, blank=True)
    VehicleYear          = models.CharField(max_length=10, blank=True)
    VehicleMake          = models.CharField(max_length=100, blank=True)
    VehicleModel         = models.CharField(max_length=100, blank=True)
    VehicleVIN           = models.CharField(max_length=100, blank=True)
    VehicleStockNumber   = models.CharField(max_length=100, blank=True)

    # ------------------------------------------------------------------
    # Sales Info
    # ------------------------------------------------------------------
    dealerid             = models.CharField(max_length=50, blank=True)
    salesperson          = models.CharField(max_length=100, blank=True)
    SalesPersonFirstName = models.CharField(max_length=100, blank=True)
    SalesPersonLastName  = models.CharField(max_length=100, blank=True)
    source               = models.CharField(max_length=255, blank=True)
    leadsourcename       = models.CharField(max_length=100, blank=True)
    LeadTypeName         = models.CharField(max_length=100, blank=True)
    LeadTypeID           = models.CharField(max_length=50, blank=True)
    leadstatustypename   = models.CharField(max_length=100, blank=True)

    # ------------------------------------------------------------------
    # Status and Timestamps
    # ------------------------------------------------------------------
    CustomerCreatedUTC   = models.CharField(max_length=50, blank=True)
    LeadCreatedUTC       = models.CharField(max_length=50, blank=True)
    SoldDateUTC          = models.CharField(max_length=50, blank=True)

    # ------------------------------------------------------------------
    # Do‑Not‑Contact Flags
    # ------------------------------------------------------------------
    DoNotCall   = models.BooleanField(default=False)
    DoNotEmail  = models.BooleanField(default=False)
    DoNotMail   = models.BooleanField(default=False)

    # ------------------------------------------------------------------
    # AI Messaging Fields
    # ------------------------------------------------------------------
    ai_message              = models.TextField(blank=True, null=True)
    message_status          = models.CharField(max_length=50, default="Not Started")
    last_texted             = models.DateTimeField(null=True, blank=True)
    follow_up_stage         = models.CharField(max_length=50, default="Day 0")
    ai_message_count        = models.PositiveIntegerField(default=0)
    opted_in_for_ai         = models.BooleanField(default=False)
    opted_out               = models.BooleanField(default=False)
    next_ai_send_at         = models.DateTimeField(null=True, blank=True)
    manual_next_ai_send_at  = models.DateTimeField(null=True, blank=True)
    ai_active               = models.BooleanField(default=True)

    # ------------------------------------------------------------------
    # Lead quality & runtime flags
    # ------------------------------------------------------------------
    score             = models.PositiveSmallIntegerField(default=0)
    has_replied       = models.BooleanField(default=False)
    new_message       = models.BooleanField(default=False)

    # ------------------------------------------------------------------
    # Catch‑all JSON for future CSV columns
    # ------------------------------------------------------------------
    extra_data        = models.JSONField(default=dict, blank=True)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.firstname} {self.lastname} – {self.cellphone}"

    def to_dict(self):
        """Return a dict ready for JSON serialization for the React UI."""
        return {
            "id": self.id,
            "name": self.name,
            "cellphone": self.cellphone,
            "email": self.email,
            "vehicle_interest": self.vehicle_interest,
            "message_status": self.message_status,
            "score": self.score,
            "last_texted": self.last_texted,
            "follow_up_stage": self.follow_up_stage,
            "opted_in_for_ai": self.opted_in_for_ai,
            "opted_out": self.opted_out,
            "ai_active": self.ai_active,
            "next_ai_send_at": self.next_ai_send_at,
            "manual_next_ai_send_at": self.manual_next_ai_send_at,
            "has_replied": self.has_replied,
            "new_message": self.new_message,
            "salesperson": self.salesperson,
            "source": self.source,
            "appointment_time": self.extra_data.get("appointment_time"),
            "tags": self.extra_data.get("tags", []),
            "ai_message": self.ai_message,
        }


class MessageLog(models.Model):
    class Direction(models.TextChoices):
        OUTBOUND = "OUT", "Outgoing"
        INBOUND = "IN", "Incoming"

    lead        = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="messages")
    content     = models.TextField()
    source      = models.CharField(
        max_length=50,
        choices=[("AI", "AI"), ("Manual", "Manual"), ("IN", "Incoming"), ("System", "System")],
        default="Manual",
    )
    from_number = models.CharField(max_length=20, blank=True, null=True)
    direction   = models.CharField(
        max_length=10,
        choices=Direction.choices,
        default=Direction.OUTBOUND,
    )
    timestamp       = models.DateTimeField(auto_now_add=True)
    sent_by_ai      = models.BooleanField(default=False)
    read            = models.BooleanField(default=False)
    twilio_sid      = models.CharField(max_length=100, blank=True, null=True)
    delivery_status = models.CharField(max_length=50, blank=True, null=True)
    follow_up_stage = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.lead.name} – {self.source} @ {self.timestamp:%Y‑%m‑%d %H:%M}"


class ScheduledEvent(models.Model):
    lead          = models.ForeignKey(Lead, on_delete=models.CASCADE)
    scheduled_for = models.DateTimeField()
    created_at    = models.DateTimeField(auto_now_add=True)
    event_type    = models.CharField(max_length=50, default="ai_follow_up")

    class Meta:
        ordering = ["scheduled_for"]

    def __str__(self):
        return f"{self.lead.name} – {self.event_type} @ {self.scheduled_for:%Y‑%m‑%d %H:%M}"


# ------------------------------------------------------------------
# Backwards‑compatibility alias for legacy imports
# ------------------------------------------------------------------
class Message(MessageLog):
    """Proxy model kept for legacy code that still imports `Message`."""

    class Meta:
        proxy = True
        verbose_name = "Message (proxy)"
        verbose_name_plural = "Messages (proxy)"
