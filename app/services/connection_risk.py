"""Connection-risk and transfer-buffer calculations.

Given two consecutive journey legs that share a city (e.g. flight lands at BLR
airport, train departs from SBC station), compute:

- the **recommended buffer** a sensible planner should leave between them
  (p90 transit time + a safety margin based on the arriving leg's delay profile)
- whether the actual inter-leg gap in the plan is ``safe | tight | risky``.

The recommendation reflects real-world variance and is what we surface in the
UI as "⚠️ This leg is delayed >1h on 40% of days — consider a 3h buffer".
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.models import TransferTime


@dataclass
class TransferInfo:
    typical_minutes: int
    p90_minutes: int
    buffer_minutes: int
    notes: Optional[str] = None


@dataclass
class RiskAssessment:
    actual_buffer_minutes: int
    recommended_buffer_minutes: int
    risk: str  # "safe" | "tight" | "risky"
    reason: str


def lookup_transfer(
    db: Session, from_code: str, to_code: str
) -> Optional[TransferInfo]:
    """Find a TransferTime row for the hub pair (either direction)."""
    if from_code == to_code:
        return TransferInfo(typical_minutes=0, p90_minutes=0, buffer_minutes=0, notes="same hub")

    row = (
        db.query(TransferTime)
        .filter(
            TransferTime.from_hub_code == from_code,
            TransferTime.to_hub_code == to_code,
        )
        .first()
    )
    if not row:
        # Try reverse direction — transit time is usually symmetric-ish
        row = (
            db.query(TransferTime)
            .filter(
                TransferTime.from_hub_code == to_code,
                TransferTime.to_hub_code == from_code,
            )
            .first()
        )
    if not row:
        return None
    return TransferInfo(
        typical_minutes=row.typical_minutes,
        p90_minutes=row.p90_minutes,
        buffer_minutes=row.buffer_minutes,
        notes=row.notes,
    )


def recommended_buffer(
    transfer: Optional[TransferInfo],
    from_leg_reliability: float = 0.85,
    from_leg_avg_delay_min: float = 0.0,
    fallback_minutes: int = 60,
) -> int:
    """How long a traveller should leave between the two legs, in minutes.

    = transfer.buffer_minutes + delay_penalty
    where delay_penalty is driven by the arriving leg's historical behaviour.
    """
    base = transfer.buffer_minutes if transfer else fallback_minutes
    # Delay penalty: if reliability < 0.9, add (1-reliability)*120 min of padding
    delay_from_reliability = max(0, int((0.9 - from_leg_reliability) * 120))
    delay_from_avg = int(from_leg_avg_delay_min or 0)
    return base + max(delay_from_reliability, delay_from_avg)


def classify(actual_minutes: int, recommended_minutes: int) -> str:
    if recommended_minutes == 0:
        return "safe"
    ratio = actual_minutes / recommended_minutes
    if ratio >= 1.0:
        return "safe"
    if ratio >= 0.7:
        return "tight"
    return "risky"


def assess(
    actual_minutes: int,
    transfer: Optional[TransferInfo],
    from_leg_reliability: float = 0.85,
    from_leg_avg_delay_min: float = 0.0,
) -> RiskAssessment:
    rec = recommended_buffer(transfer, from_leg_reliability, from_leg_avg_delay_min)
    risk = classify(actual_minutes, rec)

    typical = transfer.typical_minutes if transfer else 45
    if risk == "safe":
        reason = f"≥{rec}min buffer — comfortable"
    elif risk == "tight":
        reason = (
            f"Only {actual_minutes}min for a typically {typical}min transfer; "
            f"recommended {rec}min given delay history"
        )
    else:
        reason = (
            f"{actual_minutes}min is below the {typical}min typical transfer time. "
            f"High risk of missed connection."
        )

    return RiskAssessment(
        actual_buffer_minutes=actual_minutes,
        recommended_buffer_minutes=rec,
        risk=risk,
        reason=reason,
    )
