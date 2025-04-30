import random
from datetime import datetime
from openai import OpenAI
from dashboard.models import Lead

client = OpenAI()

# Core AI prompt builder
def build_ai_prompt(lead: Lead, followup_number=1):
    vehicle = lead.vehicle or "vehicle"
    salesperson = lead.salesperson or "one of our team members"
    lead_source = lead.source or "your online request"

    appointment_hint = "" if lead.notes is None else ("I'm available this afternoon or tomorrow if that works for you." if "appt" in lead.notes.lower() or "appointment" in lead.notes.lower() else "")

    finance_flag = "" if lead.notes is None else ("We have strong options for 84-96 month financing or trade-in deals if you're interested." if any(x in lead.notes.lower() for x in ["finance", "credit", "trade", "ltv", "term"]) else "")

    intro_variants = [
        f"Hey {lead.firstname}, just checking back in on your interest in the {vehicle}.",
        f"Hi {lead.firstname}, following up on the {vehicle} — still available if you're interested.",
        f"Good afternoon {lead.firstname}, I saw your inquiry about the {vehicle}.",
        f"{lead.firstname}, hope you’re having a good day! Wanted to reach out about the {vehicle}.",
    ]

    action_variants = [
        f"Would love to get you in for a quick test drive or talk numbers if you’re ready.",
        f"I can send you full details, pricing, or set up a time to see it in person.",
        f"If you’re still shopping, let me know what works best — I can help.",
        f"Let me know if this is still something you’re considering, and I’ll make it easy.",
    ]

    closing_variants = [
        f"– {salesperson}, Jason Pilger Chevrolet",
        f"Talk soon! {salesperson} @ Jason Pilger",
        f"Thanks again! {salesperson}, Jason Pilger Chevrolet",
        f"Let me know how I can help! – {salesperson}",
    ]

    # Build the message
    intro = random.choice(intro_variants)
    action = random.choice(action_variants)
    closing = random.choice(closing_variants)

    return f"{intro} {appointment_hint} {finance_flag} {action} {closing}"


# AI message generator
def generate_ai_message(lead: Lead, followup_number=1):
    prompt = build_ai_prompt(lead, followup_number)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly but professional car dealership assistant. Keep messages short, helpful, and encourage replies."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[ERROR] Failed to generate AI message: {str(e)}"


# Optional: used for regenerating preview
def regenerate_message(lead: Lead, followup_number=1):
    return generate_ai_message(lead, followup_number)
