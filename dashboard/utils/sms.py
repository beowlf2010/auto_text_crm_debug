
from __future__ import annotations
import logging
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger(__name__)

def send_sms(to_number: str, body: str, from_number: str | None = None, account_sid: str | None = None, auth_token: str | None = None) -> str | None:
    account_sid = account_sid or settings.TWILIO_ACCOUNT_SID
    auth_token  = auth_token or settings.TWILIO_AUTH_TOKEN
    from_number = from_number or settings.TWILIO_PHONE_NUMBER

    if not all([account_sid, auth_token, from_number]):
        logger.error("❌ Twilio config missing. Check SID, token, and phone.")
        return None

    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(to=to_number, from_=from_number, body=body)
        logger.info("✅ SMS sent ✓ SID=%s to=%s", msg.sid, to_number)
        return msg.sid
    except Exception as e:
        logger.exception("❌ Twilio send_sms failed: %s", e)
        return None
