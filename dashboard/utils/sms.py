# C:\Projects\auto_text_crm_dockerized_clean\dashboard\utils\sms.py
"""
Thin Twilio wrapper for outbound SMS.
"""

import os
import logging
from typing import Optional

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)

_SID = os.getenv("TWILIO_ACCOUNT_SID")
_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
_FROM = os.getenv("TWILIO_PHONE_NUMBER")

client: Optional[Client] = Client(_SID, _TOKEN) if _SID and _TOKEN else None


def send_sms(to_number: str, body: str) -> None:
    """Send an SMS (or log if creds missing)."""
    if client is None:
        logger.error("SMS NOT SENT – Twilio credentials missing. To=%s Body=%s", to_number, body)
        return

    try:
        msg = client.messages.create(body=body, from_=_FROM, to=to_number)
        logger.info("SMS sent sid=%s to=%s", msg.sid, to_number)
    except TwilioRestException as exc:
        logger.error("Twilio error to %s: %s", to_number, exc)
