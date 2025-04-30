# auto_text_crm/inbox/migrations/0001_initial.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    # ── the legacy ('leads', '0001_initial') dependency is gone ──
    # If your dashboard app’s first migration has a different filename,
    # adjust the second string below.
    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="InboxMessage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "direction",
                    models.CharField(
                        max_length=3,
                        choices=[("IN", "Incoming"), ("OUT", "Outgoing")],
                    ),
                ),
                (
                    "channel",
                    models.CharField(
                        max_length=10, choices=[("SMS", "SMS"), ("EMAIL", "Email")]
                    ),
                ),
                ("content", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
                (
                    "lead",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inbox_messages",
                        to="dashboard.lead",
                    ),
                ),
            ],
        ),
    ]
