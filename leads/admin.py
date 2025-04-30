from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vehicle', 'lead_source', 'status', 'created_at')
    search_fields = ('name', 'phone', 'vehicle', 'lead_source')
    list_filter = ('status', 'lead_source')
    ordering = ('-created_at',)
