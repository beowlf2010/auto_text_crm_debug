# Generated by Django 5.1.8 on 2025-04-13 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_lead_new_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='ai_message_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='lead',
            name='next_ai_send_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='opted_in_for_ai',
            field=models.BooleanField(default=False),
        ),
    ]
