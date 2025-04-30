# dashboard/utils/ai.py
# ✅ 2025‑04‑28 — fixed circular import + keyword arg mismatch
"""Utility helpers for composing AI‑generated SMS follow‑ups.

Key features
────────────
• Personalised fallback templates (name, vehicle, rep)
• SMS‑length drafts (≤65 tokens) via gpt‑4o‑mini
• Greeting normalisation & mandatory sign‑off
• Prompt + draft persisted to MessageLog for auditing
• Robust history handling → works even if old messages lack a `role` key
"""

from __future__ import annotations

import logging
import os
import re
import textwrap
from typing import Dict, List

from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─────────────────────────────────────────────────────────────────────────────
# Config / templates
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    """
    You are an upbeat yet professional automotive sales assistant.

    Craft friendly, concise SMS (25‑45 words).
    Reference the vehicle only when it adds clarity.
    Finish with an en‑dash (–) followed by the salesperson’s first name.
    Do **NOT** invent incentives or pricing not mentioned previously.
    """
)

FOLLOWUP_TEMPLATES = [
    "Hi {first}! Still thinking about the {vehicle}? Let me know if you’d like pics or a quick walk‑around video – {rep}",
    "Hey {first}, the {vehicle} is still here. Is there a good time today for a test drive? – {rep}",
    "Good news {first}! We just updated pricing on the {vehicle}. Want the details? – {rep}",
]

GREETING_REGEX = re.compile(r"^(hi|hello|hey|good\s+(morning|afternoon|evening))[\s,]*", re.I)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _display_name(lead) -> str:
    first = (getattr(lead, "first_name", "") or getattr(lead, "firstname", "")).strip()
    last  = (getattr(lead, "last_name",  "") or getattr(lead, "lastname",  "")).strip()
    if not first:
        full = (getattr(lead, "name", "") or getattr(lead, "full_name", "")).strip()
        if full:
            first = full.split(" ")[0]
    return first or last or "there"


def _rep_name(lead) -> str:
    rep = (
        getattr(lead, "salesperson", "") or getattr(lead, "assigned_salesperson", "")
    ).strip()
    return rep.split(" ")[0] if rep else getattr(settings, "SALES_REP_NAME", "Tommy")


def _normalise_msg(msg: Dict[str, str]) -> Dict[str, str]:
    """Ensure historical rows always look like {"role", "content"}."""
    role = msg.get("role")
    if not role:
        direction = str(msg.get("direction", "OUT")).upper()
        role = "user" if direction in {"IN", "INBOUND"} else "assistant"
    return {"role": role, "content": msg.get("content", "")}

# ─────────────────────────────────────────────────────────────────────────────
# Core generator
# ─────────────────────────────────────────────────────────────────────────────

def fresh_followup(lead, thread: List[Dict[str, str]], touch_num: int = 0) -> str:
    """Compose the next AI follow‑up using the last 10 messages for context."""

    display_name = _display_name(lead)
    rep_name     = _rep_name(lead)
    vehicle_txt  = getattr(lead, "vehicle_interest", "") or getattr(lead, "vehicle", "unknown")

    # Keep only the most recent 10 messages and make sure they have role/content
    safe_thread  = [_normalise_msg(m) for m in thread[-10:]]
    last_user_msg = next((m["content"] for m in reversed(safe_thread) if m["role"] == "user"), "")

    user_prompt = textwrap.dedent(
        f"""
        Lead first name: {display_name}
        Vehicle of interest: {vehicle_txt}
        Lead source: {getattr(lead, 'lead_source', getattr(lead, 'source', 'unknown'))}
        Last customer message: \"{last_user_msg}\"
        Follow‑up number: {touch_num + 1}

        Write a friendly SMS (25‑45 words), advance the conversation, include a clear question, and end with an en‑dash + {rep_name}.
        """
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=65,
        )
        draft = response.choices[0].message.content.strip()
    except Exception as exc:  # pragma: no cover
        logger.error("OpenAI error – fallback template used: %s", exc)
        draft = FOLLOWUP_TEMPLATES[touch_num % len(FOLLOWUP_TEMPLATES)].format(
            first=display_name, vehicle=vehicle_txt, rep=rep_name
        )

    # Post‑process tweaks
    draft = GREETING_REGEX.sub(f"Hi {display_name}, ", draft)
    draft = draft.replace("{vehicle}", vehicle_txt).replace("{first}", display_name).replace("{rep}", rep_name)
    if f"– {rep_name}" not in draft:
        draft = f"{draft.rstrip('– ')} – {rep_name}"

    # Log conversation prompt + draft for auditing (best‑effort, ignore failures)
    try:
        from dashboard.models import MessageLog

        MessageLog.objects.bulk_create([
            MessageLog(
                lead=lead,
                content=user_prompt,
                source="System",
                direction=MessageLog.Direction.OUTBOUND,
                sent_by_ai=False,
                read=True,
                follow_up_stage=lead.follow_up_stage,
            ),
            MessageLog(
                lead=lead,
                content=draft,
                source="AI",
                direction=MessageLog.Direction.OUTBOUND,
                sent_by_ai=True,
                read=False,
                follow_up_stage=lead.follow_up_stage,
            ),
        ])
    except Exception as exc:  # pragma: no cover
        logger.warning("Could not persist prompt/draft to MessageLog: %s", exc)

    return draft


# ---------------------------------------------------------------------------
# Legacy shim expected by older code paths (e.g. views, tasks)
# ---------------------------------------------------------------------------

def compose_outbound_text(prompt: str, thread: List[Dict[str, str]], lead):
    """Wrapper kept for backward compatibility. *prompt* is currently ignored."""
    return fresh_followup(lead, thread)

__all__ = [
    "fresh_followup",
    "compose_outbound_text",
]
