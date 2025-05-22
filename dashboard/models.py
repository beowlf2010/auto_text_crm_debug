# C:\Projects\auto_text_crm_dockerized_clean\dashboard\models.py
from __future__ import annotations

"""Django data-layer models for Auto Text CRM.

2025-05-01  — Added AI follow-up scheduling helpers
--------------------------------------------------
  • new `last_ai_sent_at` DateTimeField
  • helper trio: `compute_next_ai_send_at`, `schedule_next_ai_send`,
    `mark_ai_message_sent`
  • central `FOLLOW_UP_RULES` for easy cadence tweaks
"""

from datetime import datetime, timedelta
from uuid import uuid4

from django.db import models
from django.utils import timezone

# ───────────────────────────────────────────────────────────────────────────────
# Lead model – prospect / customer record
# ───────────────────────────────────────────────────────────────────────────────


class Lead(models.Model):
    """Represents a single lead / prospect in the system."""

    # ------------------------------------------------------------------
    # Basic Contact Info
    # ------------------------------------------------------------------
    firstname = models.CharField(max_length=100, blank=True)
    middlename = models.CharField(max_length=100, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=255, blank=True)

    email = models.EmailField(blank=True)
    emailalt = models.EmailField(blank=True)

    dayphone = models.CharField(max_length=20, blank=True)
    evephone = models.CharField(max_length=20, blank=True)
    cellphone = models.CharField(max_length=20, unique=True)

    # ------------------------------------------------------------------
    # Address Info
    # ------------------------------------------------------------------
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postalcode = models.CharField(max_length=20, blank=True)

    # ------------------------------------------------------------------
    # Vehicle Info
    # ------------------------------------------------------------------
    vehicle_interest = models.CharField(max_length=255, blank=True)
    vehicle_year = models.CharField(max_length=10, blank=True)
    vehicle_make = models.CharField(max_length=100, blank=True)
    vehicle_model = models.CharField(max_length=100, blank=True)
    vehicle_vin = models.CharField(max_length=100, blank=True)
    vehicle_stock_number = models.CharField(max_length=100, blank=True)

    # ------------------------------------------------------------------
    # Sales & source info
    # ------------------------------------------------------------------
    dealerid = models.CharField(max_length=50, blank=True)
    salesperson = models.CharField(max_length=100, blank=True)
    sales_first = models.CharField(max_length=100, blank=True)
    sales_last = models.CharField(max_length=100, blank=True)

    source = models.CharField(max_length=255, blank=True)
    leadsourcename = models.CharField(max_length=100, blank=True)
    lead_type_name = models.CharField(max_length=100, blank=True)

    # ------------------------------------------------------------------
    # Status & timestamps
    # ------------------------------------------------------------------
    customer_created_utc = models.CharField(max_length=50, blank=True)
    lead_created_utc = models.CharField(max_length=50, blank=True)
    sold_date_utc = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ------------------------------------------------------------------
    # DNC flags
    # ------------------------------------------------------------------
    do_not_call = models.BooleanField(default=False)
    do_not_email = models.BooleanField(default=False)
    do_not_mail = models.BooleanField(default=False)

    # ------------------------------------------------------------------
    # AI messaging fields
    # ------------------------------------------------------------------

    class DraftStatus(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        PENDING = "pending", "Pending Approval"
        APPROVED = "approved", "Approved"
        SENT = "sent", "Sent"

    ai_message = models.TextField(blank=True)
    ai_draft_updated_at = models.DateTimeField(null=True, blank=True)
    message_status = models.CharField(
        max_length=20, choices=DraftStatus.choices, default=DraftStatus.NOT_STARTED
    )

    last_texted = models.DateTimeField(null=True, blank=True)
    last_ai_sent_at = models.DateTimeField(null=True, blank=True)
    follow_up_stage = models.CharField(max_length=50, default="Day 0")
    ai_message_count = models.PositiveIntegerField(default=0)

    opted_in_for_ai = models.BooleanField(default=False)
    opted_out = models.BooleanField(default=False)
    ai_active = models.BooleanField(default=True)

    next_ai_send_at = models.DateTimeField(null=True, blank=True)
    manual_next_ai_send_at = models.DateTimeField(null=True, blank=True)

    # ------------------------------------------------------------------
    # Lead quality & runtime flags
    # ------------------------------------------------------------------
    score = models.PositiveSmallIntegerField(default=0)
    has_replied = models.BooleanField(default=False)
    new_message = models.BooleanField(default=False)

    # ------------------------------------------------------------------
    # Catch-all JSON for future CSV columns
    # ------------------------------------------------------------------
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    # ------------------------------------------------------------------
    # Convenience helpers (used in tasks / serializers)
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname} – {self.cellphone}"

    # ------------------------- AI follow-up helpers -------------------

    # Human-readable schedule: stage → delay (timedelta)
    FOLLOW_UP_RULES: dict[str, timedelta] = {
        "Day 0": timedelta(hours=4),      # immediate burst handled elsewhere
        "Day 1": timedelta(hours=24),
        "Day 2": timedelta(hours=24),
        "Day 3": timedelta(hours=48),
        "Week 2": timedelta(days=3),
        "Week 3+": timedelta(days=7),
    }

    def compute_next_ai_send_at(self) -> datetime | None:
        """Return the timestamp for the *next* follow-up based on current stage.

        Returns None if AI is paused / opted out.
        """
        if not self.ai_active or self.opted_out:
            return None

        # Manual override always wins
        if self.manual_next_ai_send_at:
            return self.manual_next_ai_send_at

        delay = self.FOLLOW_UP_RULES.get(self.follow_up_stage, timedelta(days=7))
        return timezone.now() + delay

    def schedule_next_ai_send(self, commit: bool = True) -> None:
        """Compute & assign `next_ai_send_at`; optionally save the model."""
        self.next_ai_send_at = self.compute_next_ai_send_at()
        if commit:
            self.save(update_fields=["next_ai_send_at"])

    def mark_ai_message_sent(self, twilio_sid: str | None = None) -> None:
        """Increment counters & advance follow-up stage after a successful send."""
        self.last_texted = self.last_ai_sent_at = timezone.now()
        self.ai_message_count += 1

        # crude stage advance; refine later if needed
        if self.follow_up_stage.startswith("Day"):
            day_num = int(self.follow_up_stage.split()[1])
            if day_num < 6:
                self.follow_up_stage = f"Day {day_num + 1}"
            else:
                self.follow_up_stage = "Week 2"
        elif self.follow_up_stage.startswith("Week"):
            self.follow_up_stage = "Week 3+"

        self.message_status = Lead.DraftStatus.SENT
        self.ai_draft_updated_at = None  # new draft required
        self.schedule_next_ai_send(commit=False)  # refresh next send time

        fields = [
            "last_texted",
            "last_ai_sent_at",
            "ai_message_count",
            "follow_up_stage",
            "message_status",
            "ai_draft_updated_at",
            "next_ai_send_at",
        ]
        self.save(update_fields=fields)

        if twilio_sid:
            # quick log entry
            Message.objects.create(
                lead=self,
                content=self.ai_message or "",
                source="AI",
                direction=Message.Direction.OUTBOUND,
                sent_by_ai=True,
                twilio_sid=twilio_sid,
                follow_up_stage=self.follow_up_stage,
            )

    # Data sent to the React UI
    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name or f"{self.firstname} {self.lastname}".strip(),
            "cellphone": self.cellphone,
            "email": self.email,
            "vehicle_interest": self.vehicle_interest,
            "message_status": self.message_status,
            "score": self.score,
            "last_texted": self.last_texted,
            "last_ai_sent_at": self.last_ai_sent_at,
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


# ───────────────────────────────────────────────────────────────────────────────
# Message model – inbound & outbound message log
# ───────────────────────────────────────────────────────────────────────────────


class Message(models.Model):
    # ─── core fields ────────────────────────────────────────────────────────────
    body        = models.TextField()
    sent_by     = models.CharField(          # replaces “direction”
        max_length=10,
        choices=(
            ("customer", "Customer"),   # inbound
            ("agent",    "Agent"),      # outbound
        )
    )

    from_number     = models.CharField(max_length=20, blank=True, null=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    twilio_sid      = models.CharField(max_length=100, blank=True, null=True)
    delivery_status = models.CharField(max_length=50,  blank=True, null=True)
    follow_up_stage = models.CharField(max_length=50,  blank=True, null=True)
    lead            = models.ForeignKey("Lead", on_delete=models.CASCADE)
    source          = models.CharField(max_length=20,  default="SMS")

    class Meta:
        ordering = ["-timestamp"]

    # ─── backward-compat props so the front-end doesn’t have to change ─────────
