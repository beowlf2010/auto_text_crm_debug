from django.contrib import admin
from .models import Lead, MessageLog

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'cellphone', 'message_status')  # fields that actually exist
    search_fields = (
        'firstname',
        'lastname',
        'cellphone',
        'email',
        'VehicleVIN',
        'VehicleStockNumber',
    )
    ordering = ('-id',)

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('lead', 'source', 'timestamp')
    ordering = ('-timestamp',)
