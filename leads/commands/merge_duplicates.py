# leads/management/commands/merge_duplicates.py

from django.core.management.base import BaseCommand
from leads.models import Lead
from django.db import transaction


class Command(BaseCommand):
    help = 'Merge duplicate leads by cellphone'

    @transaction.atomic
    def handle(self, *args, **options):
        duplicates = {}
        all_leads = Lead.objects.all()

        # Group leads by cellphone
        for lead in all_leads:
            phone = lead.cellphone.strip()
            if not phone:
                continue
            duplicates.setdefault(phone, []).append(lead)

        merged_count = 0
        for phone, leads in duplicates.items():
            if len(leads) > 1:
                # Sort by created date or ID to pick a primary
                leads.sort(key=lambda x: x.id)
                primary = leads[0]

                # Merge data into primary
                for secondary in leads[1:]:
                    # Example merge logic:
                    if not primary.firstname and secondary.firstname:
                        primary.firstname = secondary.firstname
                    if not primary.lastname and secondary.lastname:
                        primary.lastname = secondary.lastname
                    # Repeat for each field you want to merge
                    # ...

                    # After merging, you can delete the secondary record
                    secondary.delete()

                primary.save()
                merged_count += 1

        self.stdout.write(self.style.SUCCESS(f'Merged {merged_count} phone groups.'))
