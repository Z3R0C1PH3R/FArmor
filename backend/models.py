from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Policy:
    max_transaction_limit: int
    allowed_vendors: list[str]
    allowed_initiators: list[str]

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Policy":
        max_limit = int(data["max_transaction_limit"])
        allowed_vendors = [str(v).strip() for v in data["allowed_vendors"]]
        allowed_initiators = [str(i).strip() for i in data["allowed_initiators"]]
        return Policy(
            max_transaction_limit=max_limit,
            allowed_vendors=allowed_vendors,
            allowed_initiators=allowed_initiators,
        )


@dataclass(frozen=True)
class Intent:
    target_vendor: str
    payment_amount: int
    justification: str
    initiator_role: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Intent":
        return Intent(
            target_vendor=str(data["target_vendor"]).strip(),
            payment_amount=int(data["payment_amount"]),
            justification=str(data["justification"]).strip(),
            initiator_role=str(data["initiator_role"]).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_vendor": self.target_vendor,
            "payment_amount": self.payment_amount,
            "justification": self.justification,
            "initiator_role": self.initiator_role,
        }
