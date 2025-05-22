# C:\Projects\auto_text_crm_dockerized_clean\auto_text_crm\__init__.py
"""
Project package initialization for Auto Text CRM.

Keeping this minimal—just expose the Celery app so `celery -A auto_text_crm …`
and Django imports can find it.
"""

from dashboard.celery import app as celery_app  # noqa: F401

__all__ = ("celery_app",)
