# dashboard/management/commands/merge_old_leads.py
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from dashboard.models import Lead as NewLead


class Command(BaseCommand):
    help = (
        "Copy rows from the legacy leads_lead table into dashboard_lead, "
        "keyed by cellphone/phone."
    )

    def handle(self, *args, **options):
        # Check that the table exists
        if "leads_lead" not in connection.introspection.table_names():
            raise CommandError("Table leads_lead does not exist in this database.")

        # Build a column‑name map so we can handle different schemas gracefully
        col_names = {c.name for c in connection.introspection.get_table_description(connection.cursor(), "leads_lead")}

        # Choose the best available phone & email column names
        phone_col  = "cellphone" if "cellphone" in col_names else "phone"
        email_col  = "email"     if "email"     in col_names else None
        source_col = "lead_source" if "lead_source" in col_names else None
        created_col = "created_at" if "created_at" in col_names else None

        select_cols = ["name", phone_col]
        if email_col:   select_cols.append(email_col)
        if source_col:  select_cols.append(source_col)
        if created_col: select_cols.append(created_col)

        sql = f'SELECT {", ".join(select_cols)} FROM leads_lead'

        created = updated = skipped = 0

        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(sql)
            for row in cur.fetchall():
                data = dict(zip(select_cols, row))
                phone = data.pop(phone_col)
                if not phone:
                    skipped += 1
                    continue

                defaults = {
                    "name": data.get("name") or "",
                    "cellphone": phone,
                    "email": data.get(email_col, "") if email_col else "",
                    "source": data.get(source_col, "") if source_col else "",
                    "created_at": data.get(created_col) if created_col else None,
                }

                _, is_created = NewLead.objects.update_or_create(
                    cellphone=phone,
                    defaults=defaults,
                )
                if is_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Merged {created} new, {updated} updated, {skipped} skipped."
            )
        )
