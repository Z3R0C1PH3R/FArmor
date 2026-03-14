from __future__ import annotations

from dataclasses import asdict

from .models import Intent, Policy


class PolicyViolationError(Exception):
    pass


def validate_intent(intent: Intent, policy: Policy) -> dict[str, str]:
    """Deterministically validate intent against policy and return trace details."""
    if intent.payment_amount > policy.max_transaction_limit:
        raise PolicyViolationError(
            f"Blocked: payment amount ${intent.payment_amount} exceeds max "
            f"limit ${policy.max_transaction_limit}."
        )

    if intent.target_vendor not in policy.allowed_vendors:
        raise PolicyViolationError(
            f"Blocked: vendor '{intent.target_vendor}' is not in allowed vendors "
            f"{policy.allowed_vendors}."
        )

    if intent.initiator_role not in policy.allowed_initiators:
        raise PolicyViolationError(
            f"Blocked: initiator role '{intent.initiator_role}' is not in allowed initiators "
            f"{policy.allowed_initiators}."
        )

    return {
        "status": "allowed",
        "rule_check": "amount/vendor/initiator all passed",
        "intent": str(asdict(intent)),
    }
