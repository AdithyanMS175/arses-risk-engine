from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


ActivityType = Literal["transfer", "withdrawal", "deposit", "unknown"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


class RiskEvaluationRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    transaction_amount: float = Field(..., ge=0)
    location_risk: float = Field(..., ge=0, le=1)
    activity_type: ActivityType = Field(...)

    @field_validator("user_id")
    @classmethod
    def strip_user_id(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("user_id cannot be empty")
        return v2


class RiskMetadata(BaseModel):
    confidence: int = Field(..., ge=0, le=100)
    timestamp: datetime
    model_version: str
    data_completeness: int = Field(..., ge=0, le=100)


class RiskEvaluationResponse(BaseModel):
    user_id: str
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    metadata: RiskMetadata


class HealthResponse(BaseModel):
    status: Literal["ok"]
    db_enabled: bool
    db_dialect: Optional[str] = None
