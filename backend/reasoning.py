from __future__ import annotations

import re
from typing import Iterable

from .models import Intent


KNOWN_VENDORS = [
    "AWS",
    "Azure",
    "GCP",
    "Cloudflare",
    "GitHub",
    "Notion",
    "OpenAI",
    "Datadog",
]

KNOWN_ROLES = [
    "Finance Manager",
    "DevOps Bot",
    "Bot",
    "Engineer",
    "Analyst",
    "Intern",
]


class ReasoningError(Exception):
    pass


def _extract_first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else default


def _find_token(text: str, choices: Iterable[str], fallback: str) -> str:
    lower_text = text.lower()
    for choice in choices:
        if choice.lower() in lower_text:
            return choice
    return fallback


def parse_intent_from_text(prompt: str) -> Intent:
    """Mock LLM parser that converts NL text into a strict Intent model.

    This function intentionally does only reasoning/structuring and does not execute actions.
    """
    if not prompt or not prompt.strip():
        raise ReasoningError("Prompt is empty. Cannot infer intent.")

    amount_text = _extract_first_match(r"\$\s*(\d+)", prompt)
    if not amount_text:
        amount_text = _extract_first_match(r"(?:pay|transfer|send)\s+(\d+)", prompt)

    if not amount_text:
        raise ReasoningError("Could not infer payment amount from request text.")

    vendor = _find_token(prompt, KNOWN_VENDORS, fallback="Unknown Vendor")
    role = _find_token(prompt, KNOWN_ROLES, fallback="Unknown Initiator")

    justification = _extract_first_match(
        r"(?:for|because|to cover|towards)\s+(.+?)(?:\.|$)",
        prompt,
        default="Operational expense",
    )

    intent_payload = {
        "target_vendor": vendor,
        "payment_amount": int(amount_text),
        "justification": justification,
        "initiator_role": role,
    }
    return Intent.from_dict(intent_payload)
