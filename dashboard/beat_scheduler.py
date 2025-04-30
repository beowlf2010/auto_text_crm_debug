# C:\Users\beowl\OneDrive\Desktop\auto_text_crm_dockerized\dashboard\beat_scheduler.py

from celery_tasks.schedules import crontab
from auto_text_crm.celery import app

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run every day at 8:00 AM
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        auto_generate_ai_message.s(),
        name='Auto send AI messages daily at 8AM'
    )

from dashboard.tasks import auto_generate_ai_message
