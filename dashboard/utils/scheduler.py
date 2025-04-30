# C:\Projects\auto_text_crm_dockerized_clean\dashboard\utils\scheduler.py
"""
Centralised helper for deciding when the next AI follow‑up should be sent.

Usage:
    from django.utils import timezone
    from dashboard.utils.scheduler import next_send_time

    now        = timezone.now()
    nxt, stage = next_send_time(now, "Day0")
"""

from datetime import timedelta
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Follow‑up cadence (in hours after the previous send)
# ---------------------------------------------------------------------------
CADENCE = {
    "Day0":   [0, 3, 8],          # first three messages
    "Day1":   [9, 15, 19],        # next‑day triple
    "Day3":   [48, 60],           # two‑message day‑3 sequence
    "Week2":  [14 * 24, 17 * 24], # two‑message week‑2
    "Week3+": [7 * 24],           # bi‑weekly thereafter
}


# ---------------------------------------------------------------------------
# Stage progression map
# ---------------------------------------------------------------------------
PROGRESSION = {
    "Day0":  "Day1",
    "Day1":  "Day3",
    "Day3":  "Week2",
    "Week2": "Week3+",
    "Week3+": "Week3+",      # stays here forever (bi‑weekly loop)
}


# ---------------------------------------------------------------------------
def next_send_time(now, stage: str) -> Tuple[Optional[object], str]:
    """
    Given the current time and the lead's follow_up_stage, return:

        (next_datetime, new_stage)

    * If no next send is required (e.g. cadence exhausted), returns (None, stage).
    * The function is idempotent: calling it twice without updating the lead will
      keep advancing through the stage's hourly list.
    """
    hours_list = CADENCE.get(stage, [])
    if not hours_list:
        return None, stage

    next_hours = hours_list.pop(0)              # consume first offset
    new_stage = stage
    if not hours_list:                          # stage completed
        new_stage = PROGRESSION.get(stage, stage)

    return now + timedelta(hours=next_hours), new_stage
