# Philos Orientation - Logic Layer

Clean decision engine based on:
**EventZero → State → Constraints → Decision → ActionPath → History**

## Architecture

```
┌─────────────┐
│ EventZero   │  Gap between current and required state
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ State       │  Current emotional/rational/physical state
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Constraints │  Validate against moral/energy/exploitation rules
└──────┬──────┘
       │
       ├─→ BLOCKED → Recommendation
       │
       └─→ ALLOWED → ActionPath → History
```

## Core Components

### 1. Models (`models.py`)
Pure data structures:
- `EventZero`: Input event with gap analysis
- `State`: Current system state
- `ActionEvaluation`: Harm/gain metrics
- `DecisionState`: Computed decision result
- `ActionPath`: Recommended path
- `HistoryItem`: Audit record

### 2. Constraints (`constraints.py`)
Validation rules:
- **Moral Floor**: `action_harm <= 0`
- **Energy Floor**: `physical_capacity >= 20`
- **Exploitation**: `personal_gain <= collective_gain * 2`

### 3. Decision (`decision.py`)
Decision logic:
- Constraint priority resolution
- Hebrew recommendations
- Gap type → Action path mapping

### 4. History (`history.py`)
Audit trail:
- Newest first ordering
- Complete context preservation
- Filter by status/gap_type

### 5. Engine (`engine.py`)
Orchestrator:
- Complete evaluation flow
- History management
- Result composition

## Usage Example

```python
from philos_orientation import PhilosEngine, EventZero, State, ActionEvaluation

# Initialize engine
engine = PhilosEngine()

# Define input
event_zero = EventZero(
    current_state="עייף ומבולבל",
    required_state="בהיר ופעיל",
    gap_type="energy",
    urgency=75,
    scope="self"
)

state = State(
    emotional_intensity=60,
    rational_clarity=40,
    physical_capacity=15,  # Below threshold!
    chaos_order=-20,
    ego_collective=10
)

evaluation = ActionEvaluation(
    action_harm=0,
    personal_gain=30,
    collective_gain=20
)

# Evaluate
result = engine.evaluate(event_zero, state, evaluation)

# Result structure:
# {
#   'event_zero': {..., 'event_zero_summary': '...' },
#   'state': {...},
#   'evaluation': {...},
#   'decision_state': {
#     'constraints': {
#       'pass': False,
#       'reason': ['קריסת אנרגיה: capacity נמוך מדי']
#     },
#     'result': {'status': 'blocked'},
#     'recommended_action': 'צמצם היקף וחזור כשיש יותר capacity'
#   },
#   'action_path': {'visible': False, ...},
#   'history_item': {...}
# }
```

## Constraint Rules

| Constraint | Rule | Failure Message |
|------------|------|----------------|
| Moral Floor | `action_harm <= 0` | רצפה מוסרית: נזק גבוה מדי |
| Energy Floor | `physical_capacity >= 20` | קריסת אנרגיה: capacity נמוך מדי |
| Exploitation | `personal_gain <= collective_gain * 2` | ניצול: רווח אישי גבוה מדי ביחס לקולקטיבי |

## Action Paths (Gap Type Mapping)

| Gap Type | Path | First Action |
|----------|------|-------------|
| energy | מסלול גוף | בצע פעולה גופנית קצרה שמחזירה capacity |
| clarity | מסלול מחשבה | כתוב את הבעיה במשפט אחד ברור |
| order | מסלול סדר | סדר מרכיב אחד קטן במציאות |
| relation | מסלול קשר | צור קשר ישיר עם אדם אחד רלוונטי |
| collective_value | מסלול תרומה | בצע פעולה אחת שמועילה ליותר מאדם אחד |

## Decision Priority

When multiple constraints fail, recommendation follows priority:
1. **Moral Floor** (highest)
2. **Energy Floor**
3. **Exploitation** (lowest)

## History Structure

Each evaluation creates one history item with:
- Complete input context (EventZero, State, Evaluation)
- Decision result and reasons
- Recommended action
- Action path name (if allowed)
- Timestamp

Ordered newest first.

## Field Naming Stability

All field names are **fixed** and match Base44 spec:
- `current_state`, `required_state`
- `gap_type`, `urgency`, `scope`
- `emotional_intensity`, `rational_clarity`, `physical_capacity`
- `chaos_order`, `ego_collective`
- `action_harm`, `personal_gain`, `collective_gain`
- `decision_state`, `action_path`

**Do not rename or create alternatives.**

## Integration

This logic layer is:
- ✅ Framework agnostic
- ✅ Pure business logic
- ✅ No UI dependencies
- ✅ Fully typed (Pydantic)
- ✅ Testable
- ✅ Compatible with existing frontend

Can be used with:
- FastAPI endpoints
- Background workers
- CLI tools
- Testing frameworks
