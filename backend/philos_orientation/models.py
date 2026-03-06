"""Core data models for Philos Orientation system."""

from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# Enums
GapType = Literal["energy", "clarity", "order", "relation", "collective_value"]
Scope = Literal["self", "one_person", "small_group", "community"]
DecisionStatus = Literal["allowed", "blocked"]


class EventZero(BaseModel):
    """Initial event that triggers the decision process."""
    
    current_state: str
    required_state: str
    gap_type: GapType
    urgency: int = Field(ge=0, le=100)
    scope: Scope
    emotion: Optional[str] = None
    context: Optional[str] = None
    desire: Optional[str] = None
    
    @property
    def event_zero_summary(self) -> str:
        """Computed summary of the event."""
        return f"Event Zero identified: {self.gap_type} gap between current state and required state"


class State(BaseModel):
    """Current system/user state."""
    
    emotional_intensity: int = Field(ge=0, le=100)
    rational_clarity: int = Field(ge=0, le=100)
    physical_capacity: int = Field(ge=0, le=100)
    chaos_order: int = Field(ge=-100, le=100)  # -100 chaos, +100 order
    ego_collective: int = Field(ge=-100, le=100)  # -100 ego, +100 collective


class ActionEvaluation(BaseModel):
    """Evaluation of proposed action."""
    
    action_harm: int = Field(ge=0, le=100)
    personal_gain: int = Field(ge=0, le=100)
    collective_gain: int = Field(ge=0, le=100)


class ConstraintsResult(BaseModel):
    """Result of constraints validation."""
    
    pass_: bool = Field(alias="pass")
    reason: List[str] = []
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True


class DecisionResult(BaseModel):
    """Result of decision evaluation."""
    
    status: DecisionStatus


class DecisionState(BaseModel):
    """Complete decision state with recommendations."""
    
    constraints: ConstraintsResult
    result: DecisionResult
    recommended_action: str


class ActionPath(BaseModel):
    """Recommended action path when decision is allowed."""
    
    visible: bool
    path_name: str
    explanation: str
    first_action: str


class HistoryItem(BaseModel):
    """Single decision history record."""
    
    timestamp: datetime
    
    # EventZero fields
    current_state: str
    required_state: str
    gap_type: GapType
    urgency: int
    scope: Scope
    
    # State fields
    emotional_intensity: int
    rational_clarity: int
    physical_capacity: int
    chaos_order: int
    ego_collective: int
    
    # ActionEvaluation fields
    action_harm: int
    personal_gain: int
    collective_gain: int
    
    # Decision fields
    decision_status: DecisionStatus
    reasons: List[str]
    recommended_action: str
    action_path_name: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
