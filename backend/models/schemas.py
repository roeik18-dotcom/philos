"""All Pydantic models for the Philos Orientation system."""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str


class UserRegister(BaseModel):
    email: str
    password: str
    invite_code: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str
    last_login_at: Optional[str] = None

class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserResponse] = None
    token: Optional[str] = None
    message: Optional[str] = None


class DecisionRecord(BaseModel):
    action: str
    decision: str
    chaos_order: int
    ego_collective: int
    balance_score: int
    value_tag: str
    time: str
    timestamp: str

class SessionSnapshot(BaseModel):
    date: str
    timestamp: str
    totalDecisions: int
    contribution: int = 0
    recovery: int = 0
    harm: int = 0
    order: int = 0
    avoidance: int = 0

class GlobalStats(BaseModel):
    contribution: int = 0
    recovery: int = 0
    harm: int = 0
    order: int = 0
    avoidance: int = 0
    totalDecisions: int = 0
    sessions: int = 0

class PhilosSessionData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    history: List[DecisionRecord] = []
    global_stats: GlobalStats = GlobalStats()
    trend_history: List[SessionSnapshot] = []
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PhilosSyncRequest(BaseModel):
    user_id: str
    history: List[Dict[str, Any]] = []
    global_stats: Dict[str, Any] = {}
    trend_history: List[Dict[str, Any]] = []

class PhilosSyncResponse(BaseModel):
    success: bool
    user_id: str
    history: List[Dict[str, Any]] = []
    global_stats: Dict[str, Any] = {}
    trend_history: List[Dict[str, Any]] = []
    last_synced: str

class SavedSession(BaseModel):
    session_id: str
    user_id: str
    date: str
    total_decisions: int
    dominant_value: str
    order_drift: int
    collective_drift: int
    history: List[Dict[str, Any]]
    created_at: str

class SavedSessionSummary(BaseModel):
    session_id: str
    date: str
    total_decisions: int
    dominant_value: str
    order_drift: int
    collective_drift: int
    created_at: str

class SessionListResponse(BaseModel):
    success: bool

class PathSelectionRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    selected_path_id: int
    suggested_action: str
    predicted_value_tag: str
    predicted_order_drift: int
    predicted_collective_drift: int
    predicted_harm_pressure: int
    predicted_recovery_stability: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PathLearningRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    predicted_value_tag: str
    actual_value_tag: str
    predicted_order_drift: int
    actual_order_drift: int
    predicted_collective_drift: int
    actual_collective_drift: int
    predicted_harm_pressure: int
    actual_harm_pressure: int
    predicted_recovery_stability: int
    actual_recovery_stability: int
    match_quality: str  # 'high', 'medium', 'low'
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AdaptiveScores(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    contribution: int = 0
    recovery: int = 0
    order: int = 0
    harm: int = 0
    avoidance: int = 0
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DecisionRecordRequest(BaseModel):
    user_id: str
    action: str
    decision: str
    chaos_order: int
    ego_collective: int
    balance_score: int
    value_tag: str
    session_id: Optional[str] = None
    parent_decision_id: Optional[str] = None
    template_type: Optional[str] = None

class MemoryDataResponse(BaseModel):
    success: bool
    user_id: str
    learning_history: List[Dict[str, Any]] = []
    adaptive_scores: Dict[str, Any] = {}
    last_synced: str = ""



class ReplayMetadataRequest(BaseModel):
    user_id: str
    replay_of_decision_id: str
    original_value_tag: str
    alternative_path_id: int
    alternative_path_type: str
    predicted_metrics: Dict[str, Any]
    timestamp: Optional[str] = None



class ReplayInsightsResponse(BaseModel):
    success: bool
    user_id: str
    total_replays: int = 0
    # Alternative path exploration counts
    alternative_path_counts: Dict[str, int] = {}
    # Transition patterns (from -> to)
    transition_patterns: List[Dict[str, Any]] = []
    # Blind spots (patterns never explored)
    blind_spots: List[Dict[str, str]] = []
    # Most replayed decision types
    most_replayed_original_tags: Dict[str, int] = {}
    # Generated Hebrew insights
    insights: List[str] = []
    # Time-based metrics
    recent_replay_count: int = 0  # Last 7 days
    generated_at: str = ""


class FullUserDataResponse(BaseModel):
    success: bool
    user_id: str
    # Session data
    history: List[Dict[str, Any]] = []
    global_stats: Dict[str, Any] = {}
    trend_history: List[Dict[str, Any]] = []
    # Memory data  
    learning_history: List[Dict[str, Any]] = []
    adaptive_scores: Dict[str, Any] = {}
    # Session library
    saved_sessions: List[Dict[str, Any]] = []
    # Sync metadata
    last_synced: str = ""
    device_sync_status: str = "synced"


class CollectiveLayerResponse(BaseModel):
    success: bool
    total_users: int = 0
    total_decisions: int = 0
    # Value tag counts
    value_counts: Dict[str, int] = {}
    # Averages
    avg_order_drift: float = 0.0
    avg_collective_drift: float = 0.0
    avg_harm_pressure: float = 0.0
    avg_recovery_stability: float = 0.0
    # Dominant values
    dominant_value: str = ""
    dominant_direction: str = ""
    # Time-based trends (last 7 days)
    recent_trend: Dict[str, Any] = {}
    # Summary insights
    insights: List[str] = []



class DayTrend(BaseModel):
    date: str
    total_decisions: int = 0
    avg_order_drift: float = 0.0
    avg_collective_drift: float = 0.0
    avg_harm_pressure: float = 0.0
    avg_recovery_stability: float = 0.0
    value_counts: Dict[str, int] = {}

class PeriodComparison(BaseModel):
    current_period: Dict[str, Any] = {}
    previous_period: Dict[str, Any] = {}
    changes: Dict[str, Any] = {}

class CollectiveTrendsResponse(BaseModel):
    success: bool
    # Daily trends (last 14 days)
    daily_trends: List[DayTrend] = []
    # Period comparison (last 7 days vs previous 7 days)
    comparison: PeriodComparison = PeriodComparison()
    # Trend insights
    insights: List[str] = []


    """
    Get time-based collective trends and comparison views.
    Aggregates data by day and compares current period vs previous period.
    """

class OrientationFieldResponse(BaseModel):
    success: bool
    field_distribution: Dict[str, float] = {}  # direction -> percentage
    field_center: Dict[str, float] = {}        # x, y coordinates of collective center
    total_users: int = 0
    total_decisions: int = 0
    dominant_direction: Optional[str] = None
    field_momentum: Optional[str] = None       # stabilizing, drifting, shifting
    momentum_direction: Optional[str] = None   # which direction the field is moving toward
    momentum_strength: float = 0.0             # 0-100, strength of momentum
    momentum_arrow: Dict[str, float] = {}      # from_x, from_y, to_x, to_y for visualization
    field_insight: Optional[str] = None
    momentum_insight: Optional[str] = None     # specific insight about momentum

class WeeklyFieldSnapshot(BaseModel):
    week_label: str                            # "שבוע 1", "שבוע 2", etc.
    week_start: str                            # ISO date
    center_x: float
    center_y: float
    dominant_direction: Optional[str] = None
    positive_ratio: float = 0.0                # 0-100, % of positive directions
    total_actions: int = 0

class FieldHistoryResponse(BaseModel):
    success: bool
    weekly_snapshots: List[WeeklyFieldSnapshot] = []  # Last 4 weeks
    sparkline_data: List[float] = []           # positive_ratio for each week (for sparkline)
    trend_type: Optional[str] = None           # stabilizing, drifting, shifting_recovery, etc.
    trend_direction: Optional[str] = None      # Which direction trend is moving
    trend_insight: Optional[str] = None        # Hebrew insight about the trend
    weeks_analyzed: int = 0

class FieldTodayResponse(BaseModel):
    success: bool
    distribution: Dict[str, float] = {}        # direction -> percentage (only 4 positive directions)
    total_actions: int = 0
    active_users: int = 0
    dominant_direction: Optional[str] = None
    insight: Optional[str] = None              # Hebrew insight

class WeeklyInsightResponse(BaseModel):
    success: bool
    user_id: str
    distribution: Dict[str, int] = {}          # direction -> count
    distribution_percent: Dict[str, float] = {} # direction -> percentage
    total_actions: int = 0
    dominant_direction: Optional[str] = None
    insight_he: Optional[str] = None
    trend: Optional[str] = None                # improving, stable, declining

class ShareCardResponse(BaseModel):
    success: bool
    user_id: str
    orientation: Optional[str] = None          # Current dominant orientation
    message_he: Optional[str] = None           # Hebrew message for sharing
    streak: int = 0
    compass_position: Dict[str, float] = {}    # x, y for compass visualization

class OrientationIndexResponse(BaseModel):
    success: bool
    distribution: Dict[str, float] = {}        # Global distribution percentages
    dominant_direction: Optional[str] = None
    total_users: int = 0
    total_actions_today: int = 0
    yesterday_dominant: Optional[str] = None
    direction_change: Optional[str] = None     # same, shifted_to_X
    headline_he: Optional[str] = None

class DirectionPercentile(BaseModel):
    direction: str
    user_count: int                            # User's action count in this direction
    percentile: float                          # 0-100, user's percentile (higher = more focused)
    rank_label: Optional[str] = None           # "עליון 10%", "עליון 25%", etc.

class UserComparisonResponse(BaseModel):
    success: bool
    user_id: str
    total_user_actions: int = 0
    direction_percentiles: List[DirectionPercentile] = []  # Percentile for each direction
    dominant_direction: Optional[str] = None   # User's most frequent direction
    dominant_percentile: float = 0.0           # Percentile in dominant direction
    comparison_insight: Optional[str] = None   # Hebrew insight about user's position
    week_comparison: Dict[str, float] = {}     # This week vs collective average

class DecisionPathResponse(BaseModel):
    success: bool
    user_id: str
    current_state: Optional[str] = None        # Current imbalance or state
    drift_type: Optional[str] = None           # harm, avoidance, isolation, rigidity
    recommended_direction: Optional[str] = None # recovery, order, contribution, exploration
    headline: Optional[str] = None             # Short Hebrew headline
    recommended_step: Optional[str] = None     # Practical recommendation
    concrete_action: Optional[str] = None      # Specific action to take
    theory_basis: Optional[str] = None         # Why this recommendation (theory link)
    session_id: Optional[str] = None           # For tracking one per session

class OrientationSnapshot(BaseModel):
    user_id: str
    timestamp: str
    dominant_direction: Optional[str] = None
    direction_counts: Dict[str, int] = {}
    positive_ratio: float = 0.0
    avoidance_ratio: float = 0.0
    momentum: Optional[str] = None

class OrientationIdentityResponse(BaseModel):
    success: bool
    user_id: str
    identity_type: Optional[str] = None        # The computed identity type
    identity_label: Optional[str] = None       # Hebrew label for identity
    identity_description: Optional[str] = None # Hebrew description
    is_warning_state: bool = False             # True for avoidance loop
    
    # Computation inputs
    dominant_direction: Optional[str] = None
    momentum: Optional[str] = None             # stabilizing, drifting, shifting, stable
    time_in_direction: int = 0                 # Days in current dominant direction
    avoidance_ratio: float = 0.0               # 0-100, percentage of avoidance actions
    previous_dominant: Optional[str] = None    # Previous dominant direction (for transitions)
    
    # Additional context
    direction_counts: Dict[str, int] = {}
    total_actions: int = 0
    weeks_analyzed: int = 0
    insight: Optional[str] = None              # Supportive Hebrew insight

class DailyQuestionResponse(BaseModel):
    success: bool
    user_id: str
    identity: Optional[str] = None             # Current orientation identity
    question_he: Optional[str] = None          # Hebrew question based on identity
    suggested_direction: Optional[str] = None  # Direction the question aims for
    question_id: Optional[str] = None          # For tracking responses
    already_answered_today: bool = False       # If user already answered today
    streak: int = 0                            # Current consecutive days streak
    longest_streak: int = 0                    # User's longest streak ever

class UserOrientationResponse(BaseModel):
    success: bool
    user_position: Dict[str, float] = {}       # x, y coordinates
    collective_center: Dict[str, float] = {}   # x, y coordinates
    alignment_score: float = 0.0               # 0-100, how aligned with collective
    drift_pattern: Optional[str] = None        # drift detection result
    momentum: Optional[str] = None             # user's momentum
    momentum_direction: Optional[str] = None   # which direction momentum is toward
    insights: List[str] = []

class DriftDetectionResponse(BaseModel):
    success: bool
    drift_detected: bool = False
    drift_type: Optional[str] = None           # chaos, isolation, order, contribution
    drift_strength: float = 0.0                # 0-100
    recent_pattern: List[str] = []             # last 7 days pattern
    insight: Optional[str] = None

class DailyQuestionAnswerRequest(BaseModel):
    question_id: str
    response_text: Optional[str] = None
    action_taken: bool = True


