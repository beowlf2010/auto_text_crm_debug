# C:\Projects\auto_text_crm_dockerized_clean\dashboard\utils\ai.py
import logging, os
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_followup(prompt: str, history: str | None = None) -> str | None:
    """
    Returns an AI-generated SMS string or None on failure.
    """
    try:
        # Adjust model / params as needed
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=120,
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a helpful car-sales follow-up bot."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as exc:
        logger.exception("AI generation failed: %s", exc)
        return None
