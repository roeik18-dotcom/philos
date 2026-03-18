"""Risk Signal data models — Pydantic schemas for the risk-signal framework."""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class SignalCategory(str, Enum):
    trust_manipulation = "trust_manipulation"
    content_integrity = "content_integrity"
    account_behavior = "account_behavior"
    network_anomaly = "network_anomaly"


class SignalSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class SignalStatus(str, Enum):
    active = "active"
    resolved = "resolved"
    dismissed = "dismissed"


class RiskSignalOut(BaseModel):
    signal_id: str
    signal_type: str
    category: str
    severity: str
    subject_user_id: str
    related_user_ids: list = []
    related_action_ids: list = []
    evidence: dict = {}
    status: str = "active"
    system_response: str = ""
    created_at: str = ""
    resolved_at: Optional[str] = None
    expires_at: Optional[str] = None


class UpdateSignalStatus(BaseModel):
    status: str
    resolution_note: str = ""
