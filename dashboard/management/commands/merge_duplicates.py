from django.core.management.base import BaseCommand
from django.db.models import Count
from dashboard.models import Lead

class Command(BaseCommand):
    help = "Merge duplicate leads that share the same phone number."

    def handle(self, *args, **options):
        ...
        # merging logic
