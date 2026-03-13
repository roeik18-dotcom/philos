"""Pydantic models for the Value + Risk + Trust system."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class ActionCreate(BaseModel):
    action_type: str  # help / create / explore / contribute
    impact: float = Field(ge=0, le=100)
    authenticity: float = Field(ge=0, le=1)


class ActionResponse(BaseModel):
    id: str
    user_id: str
    action_type: str
    impact: float
    authenticity: float
    value: float
    timestamp: str


class RiskSignalCreate(BaseModel):
    user_id: str
    signal_type: str  # manipulation / aggression / spam / deception / disruption
    confidence: float = Field(ge=0, le=1)
    severity: float = Field(ge=0, le=10)


class RiskSignalResponse(BaseModel):
    id: str
    user_id: str
    signal_type: str
    confidence: float
    severity: float
    risk: float
    timestamp: str


class TrustProfileResponse(BaseModel):
    user_id: str
    value_score: float
    risk_score: float
    trust_score: float
    total_actions: int
    total_risk_signals: int
    last_updated: str
    recent_actions: List[ActionResponse] = []
    recent_risk_signals: List[RiskSignalResponse] = []


class LedgerEntry(BaseModel):
    id: str
    user_id: str
    source_flow: str
    action_type: str
    impact: float
    authenticity: float
    computed_value_delta: float
    computed_risk_delta: float
    trust_score_after: float
    timestamp: str
    metadata: dict = {}


class TrustHistoryResponse(BaseModel):
    user_id: str
    value_score: float
    risk_score: float
    trust_score: float
    total_ledger_entries: int
    summary_by_source: dict = {}
    summary_by_action_type: dict = {}
    ledger: List[LedgerEntry] = []
