from __future__ import annotations

from dataclasses import asdict

from backend.enforcement import PolicyViolationError
from backend.models import Policy
from backend.reasoning import parse_intent_from_text
from backend.server import load_policies
from backend.execution import execute_transfer
from backend.enforcement import validate_intent


def run_case(title: str, request_text: str, policy: Policy) -> None:
    print("\n" + "=" * 72)
    print(f"CASE: {title}")
    print(f"Request: {request_text}")
    print(f"Policy: {asdict(policy)}")

    intent = parse_intent_from_text(request_text)
    print(f"Parsed intent: {asdict(intent)}")

    try:
        trace = validate_intent(intent, policy)
        receipt = execute_transfer(intent)
        print(f"Decision: ALLOWED ({trace['rule_check']})")
        print(f"Receipt created: {receipt}")
    except PolicyViolationError as err:
        print(f"Decision: BLOCKED ({err})")


def run_demo() -> None:
    policies = load_policies()

    run_case(
        "Allowed action",
        "I am the DevOps Bot, pay $400 to AWS for hosting.",
        policies["default"],
    )

    run_case(
        "Blocked action (limit violation)",
        "I am the Engineer, pay $900 to AWS for urgent capacity.",
        policies["default"],
    )

    run_case(
        "Delegation boundary violation",
        "I am the Bot, pay $500 to AWS for delegated cloud bill.",
        policies["delegated_bot"],
    )


if __name__ == "__main__":
    run_demo()
