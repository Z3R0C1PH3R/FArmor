# FArmor Short Report

## 1) Intent Model

`Intent` fields:
- `target_vendor: str`
- `payment_amount: int`
- `justification: str`
- `initiator_role: str`

The reasoning layer parses natural language into this strict structure before any action can be attempted.

## 2) Policy Model

`Policy` fields:
- `max_transaction_limit: int`
- `allowed_vendors: list[str]`
- `allowed_initiators: list[str]`

Defined in `data/policies.json` and loaded at runtime.

## 3) Enforcement Mechanism

Enforcement runs in `backend/enforcement.py` as deterministic checks:
1. `payment_amount <= max_transaction_limit`
2. `target_vendor in allowed_vendors`
3. `initiator_role in allowed_initiators`

If any check fails, the system raises `PolicyViolationError` with a clear reason. The backend returns `decision: blocked` and the reason in API response.

## 4) Demonstrated Runtime Outcomes

1. Allowed action:
- Request: `I am the DevOps Bot, pay $400 to AWS for hosting.`
- Policy: `default` (max 500)
- Result: `allowed`, receipt file created in `receipts/`

2. Blocked action (limit violation):
- Request: `I am the Engineer, pay $900 to AWS for urgent capacity.`
- Policy: `default` (max 500)
- Result: `blocked` with deterministic reason (`exceeds max limit`)

3. Delegation boundary violation:
- Request: `I am the Bot, pay $500 to AWS for delegated cloud bill.`
- Policy: `delegated_bot` (max 100)
- Result: `blocked`, proving bounded delegated authority

## 5) Traceability and Evidence

- Policy decisions are observable in JSON responses on the frontend.
- Successful actions write physical receipts with UTC timestamps to local disk.
- Architecture clearly separates reasoning, enforcement, and execution.

## 6) Implementation Summary

FArmor delivers a complete intent-aware execution workflow with structured reasoning output, deterministic policy enforcement, and verifiable runtime actions. The system is organized for clear architectural review, practical demonstration, and straightforward extension to additional policies and execution targets.
