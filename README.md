# Auto Text CRM

## Setup Instructions
1. `pip install -r requirements.txt`
2. Configure `.env` file
3. Run migrations: `python manage.py migrate`
4. Start Redis
5. Start Celery worker & beat
6. Run the Django server

Don't forget to configure your webhook URL in Twilio!
