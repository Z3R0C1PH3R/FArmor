from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path

from .models import Intent


RECEIPT_DIR = Path(__file__).resolve().parent.parent / "receipts"


def execute_transfer(intent: Intent) -> Path:
    """Simulate transfer by writing a verifiable local receipt file."""
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
    receipt_path = RECEIPT_DIR / f"receipt_{timestamp}.txt"

    body = "\n".join(
        [
            "FArmor Payment Receipt",
            "=======================",
            f"timestamp_utc={datetime.now(UTC).isoformat()}",
            f"vendor={intent.target_vendor}",
            f"amount={intent.payment_amount}",
            f"initiator_role={intent.initiator_role}",
            f"justification={intent.justification}",
            "status=EXECUTED",
        ]
    )
    receipt_path.write_text(body + "\n", encoding="utf-8")
    return receipt_path
