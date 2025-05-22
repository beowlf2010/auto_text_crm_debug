from django.contrib import admin
from .models import Lead, Message


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """
    Keeps the original column names that the UI expects, but supplies
    shim methods so Django admin finds them (avoids admin.E108 errors).
    """
    list_display = (
        "id",
        "firstname",
        "lastname",
        "cellphone",
        "message_status",
        "next_ai_send_at",
    )
    search_fields = (
        "firstname",
        "lastname",
        "cellphone",
        "email",
        "vehicle_vin",
        "vehicle_stock_number",
    )
    ordering = ("-id",)

    # ───────── shim columns ─────────
    def firstname(self, obj):
        return getattr(obj, "first_name", (obj.name or "").split(" ")[0])

    def lastname(self, obj):
        return getattr(obj, "last_name", " ")

    def cellphone(self, obj):
        return getattr(obj, "phone", "")

    def message_status(self, obj):
        return getattr(obj, "draft_status", "—")

    firstname.short_description = "First Name"
    lastname.short_description = "Last Name"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("lead", "source", "timestamp")
    ordering = ("-timestamp",)
    list_filter = ("source",)
    search_fields = ("body",)
