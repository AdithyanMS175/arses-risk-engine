from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from database import Evaluation, db_info, get_session
from models import HealthResponse, RiskEvaluationRequest, RiskEvaluationResponse
from scoring_engine import evaluate


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    enabled, dialect = db_info()
    return HealthResponse(status="ok", db_enabled=enabled, db_dialect=dialect)


@router.post("/evaluate-risk", response_model=RiskEvaluationResponse)
def evaluate_risk(payload: RiskEvaluationRequest) -> RiskEvaluationResponse:
    try:
        result = evaluate(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk evaluation failed: {e}") from e

   
    try:
        with get_session() as session:
            session.add(
                Evaluation(
                    user_id=result.user_id,
                    risk_score=result.risk_score,
                    risk_level=result.risk_level,
                    created_at=datetime.fromisoformat(
                        result.metadata.timestamp.isoformat()
                    ),
                    metadata_json=result.metadata.model_dump(mode="json"),
                )
            )
    except Exception:
        pass

    return result

