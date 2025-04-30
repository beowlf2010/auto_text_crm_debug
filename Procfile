web: gunicorn auto_text_crm.wsgi
worker: celery -A auto_text_crm worker --loglevel=info
beat: celery -A auto_text_crm beat --loglevel=info
