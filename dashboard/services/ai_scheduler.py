# C:\Projects\auto_text_crm_dockerized_clean\dashboard\services\ai_scheduler.py
"""
Central brain that decides:
• which follow‑up stage comes next
• when the next message should go out
• jittering inside the allowed send window (08:00‑19:00 local)

Usage
-----
    from dashboard.services.ai_scheduler import get_next_send

    next_dt, next_stage = get_next_send(
        current_stage="Day 0",
        last_send_at=datetime_obj,   # or None if first time
        lead_created=lead.created_at
    )
"""

import random
from datetime import datetime, timedelta, time
from typing import Tuple, Optional

import pytz
from django.conf import settings

# ----------------------------------------------------------------------
#  Cadence map – expand freely later
#  key = current stage      value = (days_delay, next_stage)
# ----------------------------------------------------------------------
CADENCE = {
    "Day 0":          (0.0,  "Day 0 – Msg 2"),   # three messages on Day‑0
    "Day 0 – Msg 2":  (0.0,  "Day 0 – Msg 3"),
    "Day 0 – Msg 3":  (1.0,  "Day 1 – Msg 1"),
    "Day 1 – Msg 1":  (0.5,  "Day 1 – Msg 2"),   # 12 h later
    "Day 1 – Msg 2":  (0.5,  "Day 1 – Msg 3"),
    "Day 1 – Msg 3":  (1.0,  "Day 2 – Msg 1"),
    "Day 2 – Msg 1":  (0.5,  "Day 2 – Msg 2"),
    "Day 2 – Msg 2":  (1.0,  "Day 3 – Msg 1"),
    # … continue through Week‑6 as you wish …
    "Week 6 – Msg N": (14.0, None),              # end of cadence
}

# Allowed send window (24‑hour clock, local time)
SEND_START = time(8, 0)   # 08:00
SEND_END   = time(19, 0)  # 19:00


def _random_time_within_window(day: datetime) -> datetime:
    """Return a datetime on the same calendar day but random time within SEND_*."""
    tz = pytz.timezone(settings.TIME_ZONE)
    start_dt = tz.localize(datetime.combine(day.date(), SEND_START))
    end_dt   = tz.localize(datetime.combine(day.date(), SEND_END))

    delta_sec = int((end_dt - start_dt).total_seconds())
    offset    = random.randint(0, delta_sec)
    return start_dt + timedelta(seconds=offset)


def clamp_to_window(dt: datetime) -> datetime:
    """If dt lands outside SEND_* window, move to the next valid window start."""
    local = pytz.timezone(settings.TIME_ZONE).normalize(dt)

    if SEND_START <= local.time() <= SEND_END:
        return local

    # if before window, push to today 08:00
    if local.time() < SEND_START:
        return local.replace(hour=SEND_START.hour, minute=0, second=0, microsecond=0)

    # else after 19:00 – move to tomorrow 08:00
    next_day = local + timedelta(days=1)
    return next_day.replace(hour=SEND_START.hour, minute=0, second=0, microsecond=0)


# ----------------------------------------------------------------------
#  Public API
# ----------------------------------------------------------------------
def get_next_send(
    current_stage: str,
    last_send_at: Optional[datetime],
    lead_created: datetime,
) -> Tuple[Optional[datetime], Optional[str]]:
    """
    Return (next_datetime, next_stage). If None is returned for stage, cadence is over.
    """
    if current_stage not in CADENCE:
        # Unknown stage – restart cadence at Day‑0
        current_stage = "Day 0"

    days_delay, next_stage = CADENCE[current_stage]

    # base date = last send time or lead creation
    base = last_send_at or lead_created
    target_day = base + timedelta(days=days_delay)

    # randomize send time for human‑like distribution
    proposed_dt = _random_time_within_window(target_day)
    proposed_dt = clamp_to_window(proposed_dt)

    return proposed_dt, next_stage
