from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Tuple

from models import RiskEvaluationRequest, RiskEvaluationResponse, RiskMetadata, RiskLevel


MODEL_VERSION = "ARS-1.0"


@dataclass(frozen=True)
class Weights:
    transaction_amount_weight: float = 0.4
    location_risk_weight: float = 0.3
    activity_risk_weight: float = 0.3


ACTIVITY_RISK: Dict[str, float] = {
    "transfer": 0.7,
    "withdrawal": 0.5,
    "deposit": 0.2,
    "unknown": 0.6,
}


def normalize_transaction_amount(amount: float) -> float:
    """
    Normalize amount into [0, 1] bucket score.

    0–1000    → 0.1
    1000–10000→ 0.5
    10000+    → 1.0
    """
    if amount <= 1000:
        return 0.1
    if amount <= 10000:
        return 0.5
    return 1.0


def risk_level_from_score(score_0_100: int) -> RiskLevel:
    if score_0_100 <= 33:
        return "LOW"
    if score_0_100 <= 66:
        return "MEDIUM"
    return "HIGH"


def calculate_data_completeness(req: RiskEvaluationRequest) -> int:
    """
    Simple completeness heuristic:
    - 4 inputs (user_id, transaction_amount, location_risk, activity_type)
    - Each contributes 25% if present and valid-ish.
    Pydantic already validates core ranges, so this mainly rewards non-empty user_id.
    """
    filled = 0
    filled += 1 if req.user_id.strip() else 0
    filled += 1 if req.transaction_amount is not None else 0
    filled += 1 if req.location_risk is not None else 0
    filled += 1 if req.activity_type is not None else 0
    return int(round((filled / 4) * 100))


def score_request(
    req: RiskEvaluationRequest, *, weights: Weights = Weights()
) -> Tuple[int, RiskLevel, RiskMetadata]:
    tx_norm = normalize_transaction_amount(req.transaction_amount)
    activity_risk = ACTIVITY_RISK.get(req.activity_type, ACTIVITY_RISK["unknown"])

    risk_score_f = (
        tx_norm * weights.transaction_amount_weight
        + req.location_risk * weights.location_risk_weight
        + activity_risk * weights.activity_risk_weight
    ) * 100.0

    risk_score = int(round(risk_score_f))
    risk_score = max(0, min(100, risk_score))

    risk_level = risk_level_from_score(risk_score)

    confidence = random.randint(70, 95)
    metadata = RiskMetadata(
        confidence=confidence,
        timestamp=datetime.now(timezone.utc),
        model_version=MODEL_VERSION,
        data_completeness=calculate_data_completeness(req),
    )

    return risk_score, risk_level, metadata


def evaluate(req: RiskEvaluationRequest) -> RiskEvaluationResponse:
    risk_score, risk_level, metadata = score_request(req)
    return RiskEvaluationResponse(
        user_id=req.user_id,
        risk_score=risk_score,
        risk_level=risk_level,
        metadata=metadata,
    )
