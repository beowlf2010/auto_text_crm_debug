# C:\Projects\auto_text_crm_dockerized_clean\Procfile
web: gunicorn AutoTextCRM.wsgi:application --bind 0.0.0.0:%PORT%
worker: celery -A AutoTextCRM worker --loglevel=info --pool=solo
beat: celery -A AutoTextCRM beat --loglevel=info
release: python manage.py migrate --noinput
