# Decision Replay System Documentation

## Philos Orientation - Replay & Counterfactual Analysis

**Version:** 1.0  
**Last Updated:** March 2026  
**Status:** Production Ready

---

## 1. Replay System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐  │
│  │ DecisionHistorySection│───▶│    DecisionReplaySection         │  │
│  │                      │    │                                    │  │
│  │ • Display history    │    │ • Original decision card          │  │
│  │ • "בדוק מסלול חלופי" │    │ • Alternative paths (2-3)         │  │
│  │   button per item    │    │ • Predicted metrics               │  │
│  └──────────────────────┘    │ • Hebrew insight generation       │  │
│                              └──────────────────────────────────┘  │
│                                          │                          │
│                                          ▼                          │
│                         ┌────────────────────────────┐              │
│                         │     usePhilosState.js      │              │
│                         │                            │              │
│                         │ • handleReplayDecision()   │              │
│                         │ • closeReplay()            │              │
│                         │ • saveReplayMetadata()     │              │
│                         │ • replayDecision state     │              │
│                         │ • replayHistory state      │              │
│                         └────────────────────────────┘              │
│                                          │                          │
└──────────────────────────────────────────│──────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     FastAPI (server.py)                       │  │
│  │                                                                │  │
│  │  POST /api/memory/replay      - Save replay metadata          │  │
│  │  GET  /api/memory/replays/{user_id} - Get replay history      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                          │                          │
└──────────────────────────────────────────│──────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       DATABASE LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    MongoDB Collections                         │  │
│  │                                                                │  │
│  │  philos_replays     - Replay metadata records                 │  │
│  │  philos_decisions   - Original decision records (reference)   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Replay Data Model

### 2.1 Replay Metadata Schema

```javascript
{
  // Unique identifier for replay record
  "id": "uuid-v4",
  
  // User who performed the replay
  "user_id": "string",
  
  // Reference to original decision being replayed
  "replay_of_decision_id": "string (decision.id)",
  
  // Value tag of the original decision
  "original_value_tag": "contribution|recovery|order|harm|avoidance",
  
  // Which alternative path was selected for exploration
  "alternative_path_id": "integer (1-3)",
  
  // Type of alternative path explored
  "alternative_path_type": "contribution|recovery|order|harm|avoidance",
  
  // Predicted metrics for the alternative path
  "predicted_metrics": {
    "orderDrift": "integer (-100 to 100)",
    "collectiveDrift": "integer (-100 to 100)",
    "harmPressure": "float",
    "recoveryStability": "float",
    "predictedOrder": "integer",
    "predictedCollective": "integer",
    "predictedBalance": "integer (0-100)",
    "balanceDiff": "integer (difference from original)"
  },
  
  // When the replay was performed
  "timestamp": "ISO 8601 datetime",
  
  // When the record was created in database
  "created_at": "ISO 8601 datetime"
}
```

### 2.2 Alternative Path Schema (Generated Client-Side)

```javascript
{
  "id": "integer (1-3)",
  "type": "contribution|recovery|order|harm|avoidance",
  "hebrewName": "מסלול תרומה|מסלול התאוששות|מסלול סדר|מסלול נזק|מסלול הימנעות",
  "action": "string (suggested action in Hebrew)",
  "description": "string (path description in Hebrew)",
  "valueTag": "string (same as type)",
  "metrics": {
    "orderDrift": "integer",
    "collectiveDrift": "integer",
    "harmPressure": "float",
    "recoveryStability": "float",
    "predictedOrder": "integer",
    "predictedCollective": "integer",
    "predictedBalance": "integer",
    "balanceDiff": "integer"
  }
}
```

---

## 3. Replay Metadata Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | UUID | Unique identifier for the replay record | Auto-generated |
| `user_id` | String | User performing the replay | Yes |
| `replay_of_decision_id` | String | ID of the original decision | Yes |
| `original_value_tag` | Enum | Value tag of original decision | Yes |
| `alternative_path_id` | Integer | Selected alternative path (1-3) | Yes |
| `alternative_path_type` | Enum | Type of alternative explored | Yes |
| `predicted_metrics` | Object | Predicted outcomes for alternative | Yes |
| `timestamp` | DateTime | When replay occurred | Auto-generated |
| `created_at` | DateTime | Database insertion time | Auto-generated |

### Value Tag Enum Values

| Value | Hebrew Label | Description |
|-------|--------------|-------------|
| `contribution` | מסלול תרומה | Actions oriented toward helping others |
| `recovery` | מסלול התאוששות | Actions for rest and recuperation |
| `order` | מסלול סדר | Actions that increase structure |
| `harm` | מסלול נזק | Actions that may cause damage |
| `avoidance` | מסלול הימנעות | Actions of avoidance or delay |

---

## 4. Replay API Endpoints

### 4.1 Save Replay Metadata

**Endpoint:** `POST /api/memory/replay`

**Request Body:**
```json
{
  "user_id": "user-123",
  "replay_of_decision_id": "dec_1709981234567_abc123",
  "original_value_tag": "avoidance",
  "alternative_path_id": 1,
  "alternative_path_type": "recovery",
  "predicted_metrics": {
    "orderDrift": -5,
    "collectiveDrift": 0,
    "harmPressure": -20,
    "recoveryStability": 20,
    "predictedOrder": -5,
    "predictedCollective": 0,
    "predictedBalance": 95,
    "balanceDiff": 15
  },
  "timestamp": "2026-03-09T10:30:00.000Z"
}
```

**Response:**
```json
{
  "success": true,
  "id": "4be80b43-e98f-4168-b455-20433a175630",
  "timestamp": "2026-03-09T10:30:00.000Z"
}
```

### 4.2 Get Replay History

**Endpoint:** `GET /api/memory/replays/{user_id}?limit=50`

**Parameters:**
- `user_id` (path): User identifier
- `limit` (query, optional): Maximum records to return (default: 50)

**Response:**
```json
{
  "success": true,
  "user_id": "user-123",
  "replays": [
    {
      "id": "uuid",
      "replay_of_decision_id": "dec_123",
      "original_value_tag": "avoidance",
      "alternative_path_id": 1,
      "alternative_path_type": "recovery",
      "predicted_metrics": {...},
      "timestamp": "2026-03-09T10:30:00.000Z"
    }
  ],
  "total_replays": 15,
  "pattern_counts": {
    "avoidance_to_recovery": 5,
    "harm_to_contribution": 3,
    "avoidance_to_order": 7
  }
}
```

---

## 5. Replay Flow

### 5.1 User Interaction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER JOURNEY                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. USER MAKES DECISION                                         │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ Action: "התעלמתי מהבעיה" (I ignored the problem)    │     │
│     │ Value Tag: avoidance                                 │     │
│     │ Balance: 80                                          │     │
│     └─────────────────────────────────────────────────────┘     │
│                              │                                   │
│                              ▼                                   │
│  2. DECISION APPEARS IN HISTORY                                 │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ [Decision Card]                                      │     │
│     │ • הימנעות (avoidance badge)                         │     │
│     │ • [הוסף המשך] [בדוק מסלול חלופי]                    │     │
│     └─────────────────────────────────────────────────────┘     │
│                              │                                   │
│                              ▼                                   │
│  3. USER CLICKS "בדוק מסלול חלופי"                              │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ DecisionReplaySection opens                          │     │
│     │                                                      │     │
│     │ ┌─────────────────────────────────────────────┐     │     │
│     │ │ ההחלטה המקורית (Original Decision)          │     │     │
│     │ │ "התעלמתי מהבעיה"                            │     │     │
│     │ │ הימנעות | איזון: 80                         │     │     │
│     │ └─────────────────────────────────────────────┘     │     │
│     │                                                      │     │
│     │ מסלולים חלופיים אפשריים:                            │     │
│     │ ┌─────────────────────────────────────────────┐     │     │
│     │ │ מסלול תרומה    | +20 איזון                  │     │     │
│     │ │ מסלול סדר      | -15 איזון                  │     │     │
│     │ │ מסלול נזק      | -25 איזון                  │     │     │
│     │ └─────────────────────────────────────────────┘     │     │
│     └─────────────────────────────────────────────────────┘     │
│                              │                                   │
│                              ▼                                   │
│  4. USER SELECTS ALTERNATIVE PATH                               │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ תובנה (Insight):                                    │     │
│     │ "אם היית בוחר במסלול התאוששות, לחץ הנזק היה        │     │
│     │  נמוך יותר."                                        │     │
│     └─────────────────────────────────────────────────────┘     │
│                              │                                   │
│                              ▼                                   │
│  5. REPLAY METADATA SAVED                                       │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ POST /api/memory/replay                              │     │
│     │ {                                                    │     │
│     │   replay_of_decision_id: "dec_xxx",                 │     │
│     │   original_value_tag: "avoidance",                  │     │
│     │   alternative_path_type: "recovery",                │     │
│     │   predicted_metrics: {...}                          │     │
│     │ }                                                    │     │
│     └─────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow Sequence

```
User Action          Frontend                    Backend              Database
    │                   │                           │                    │
    │ Click replay btn  │                           │                    │
    │──────────────────▶│                           │                    │
    │                   │                           │                    │
    │                   │ handleReplayDecision()    │                    │
    │                   │ setReplayDecision(item)   │                    │
    │                   │                           │                    │
    │                   │ generateAlternativePaths()│                    │
    │                   │ (client-side generation)  │                    │
    │                   │                           │                    │
    │◀──────────────────│ Render DecisionReplaySection                   │
    │                   │                           │                    │
    │ Select alt path   │                           │                    │
    │──────────────────▶│                           │                    │
    │                   │                           │                    │
    │                   │ generateInsightText()     │                    │
    │                   │ saveReplayMetadata()      │                    │
    │                   │                           │                    │
    │                   │ POST /api/memory/replay   │                    │
    │                   │──────────────────────────▶│                    │
    │                   │                           │                    │
    │                   │                           │ Insert into        │
    │                   │                           │ philos_replays     │
    │                   │                           │───────────────────▶│
    │                   │                           │                    │
    │                   │◀──────────────────────────│ {success, id}      │
    │                   │                           │                    │
    │◀──────────────────│ Show insight text         │                    │
    │                   │                           │                    │
```

---

## 6. Replay Storage Logic

### 6.1 Client-Side State Management

```javascript
// usePhilosState.js

// State variables for replay
const [replayDecision, setReplayDecision] = useState(null);
const [replayHistory, setReplayHistory] = useState([]);

// Trigger replay for a decision
const handleReplayDecision = (decision) => {
  setReplayDecision(decision);
  // Auto-scroll to replay section
};

// Close replay section
const closeReplay = () => {
  setReplayDecision(null);
};

// Save replay metadata to backend + local state
const saveReplayMetadata = async (replayData) => {
  // 1. Attempt cloud save
  await fetch('/api/memory/replay', {
    method: 'POST',
    body: JSON.stringify({ user_id, ...replayData })
  });
  
  // 2. Update local replay history (max 50 entries)
  setReplayHistory(prev => [replayData, ...prev].slice(0, 50));
};
```

### 6.2 Backend Storage Logic

```python
# server.py

@api_router.post("/memory/replay")
async def save_replay_metadata(data: ReplayMetadataRequest):
    """
    Storage logic:
    1. Generate unique ID
    2. Add timestamps
    3. Insert into philos_replays collection
    4. Return success response
    """
    doc = {
        'id': str(uuid.uuid4()),
        'user_id': data.user_id,
        'replay_of_decision_id': data.replay_of_decision_id,
        'original_value_tag': data.original_value_tag,
        'alternative_path_id': data.alternative_path_id,
        'alternative_path_type': data.alternative_path_type,
        'predicted_metrics': data.predicted_metrics,
        'timestamp': data.timestamp or now.isoformat(),
        'created_at': now.isoformat()
    }
    
    await db.philos_replays.insert_one(doc)
    return {"success": True, "id": doc['id']}
```

### 6.3 MongoDB Collection Structure

```javascript
// Collection: philos_replays
// Indexes recommended:
//   - user_id (for user queries)
//   - timestamp (for sorting)
//   - original_value_tag (for pattern analysis)

{
  "_id": ObjectId("..."),
  "id": "4be80b43-e98f-4168-b455-20433a175630",
  "user_id": "user-123",
  "replay_of_decision_id": "dec_1709981234567_abc123",
  "original_value_tag": "avoidance",
  "alternative_path_id": 1,
  "alternative_path_type": "recovery",
  "predicted_metrics": {
    "orderDrift": -5,
    "collectiveDrift": 0,
    "harmPressure": -20,
    "recoveryStability": 20,
    "predictedOrder": -5,
    "predictedCollective": 0,
    "predictedBalance": 95,
    "balanceDiff": 15
  },
  "timestamp": "2026-03-09T10:30:00.000Z",
  "created_at": "2026-03-09T10:30:00.000Z"
}
```

---

## 7. How Replay Data Feeds Behavioral Analysis

### 7.1 Pattern Recognition

The replay system tracks **transition patterns** between original decisions and explored alternatives:

```
Pattern Format: {original_value_tag}_to_{alternative_path_type}

Example patterns:
- avoidance_to_recovery  → User often wonders about recovery alternatives
- harm_to_contribution   → User explores positive alternatives after negative actions
- order_to_avoidance     → User considers less structured approaches
```

### 7.2 Behavioral Insights Derivation

```javascript
// Pattern analysis from GET /api/memory/replays/{user_id}

{
  "pattern_counts": {
    "avoidance_to_recovery": 12,    // Most explored pattern
    "avoidance_to_order": 8,
    "harm_to_contribution": 5,
    "recovery_to_order": 3
  }
}

// Insights that can be derived:
// 1. "You often explore recovery alternatives after avoidance decisions"
// 2. "Your replay patterns suggest interest in more structured approaches"
// 3. "You rarely explore contribution paths from order decisions"
```

### 7.3 Integration with Existing Analysis Systems

| System | How Replay Data Integrates |
|--------|---------------------------|
| **Path Learning Layer** | Replay patterns inform which paths users wish they had taken |
| **Adaptive Path Engine** | Frequently explored alternatives can boost path suggestions |
| **Weekly Behavioral Report** | Include "most replayed decisions" and "preferred alternatives" |
| **Chain Insights** | Track if replayed decisions are part of chains |
| **Personal Map** | Show replay patterns on the personal value map |

### 7.4 Data Flow to Reports

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  philos_replays │────▶│ Pattern Analysis│────▶│ Behavioral      │
│  Collection     │     │                 │     │ Reports         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │ Hebrew Insights │
                        │                 │
                        │ "אתה נוטה לבחון │
                        │  מסלולי התאוששות│
                        │  אחרי החלטות    │
                        │  הימנעות"       │
                        └─────────────────┘
```

---

## 8. Replay Insights Summary (IMPLEMENTED)

### 8.1 Feature Overview

A dedicated dashboard section that aggregates and visualizes replay exploration patterns, providing meta-level insights about decision-making tendencies.

**Status:** ✅ Fully Implemented

### 8.2 Implemented UI Components

```
┌─────────────────────────────────────────────────────────────────┐
│               סיכום תובנות הפעלה חוזרת                          │
│               (Replay Insights Summary)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ המסלולים החלופיים הנבדקים ביותר                         │   │
│  │ (Most Explored Alternative Paths)                        │   │
│  │                                                          │   │
│  │  1. התאוששות (Recovery)     ████████████  42%           │   │
│  │  2. סדר (Order)             ████████      28%           │   │
│  │  3. תרומה (Contribution)    ██████        20%           │   │
│  │  4. אחר (Other)             ███           10%           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ דפוסי מעבר נפוצים                                       │   │
│  │ (Common Transition Patterns)                             │   │
│  │                                                          │   │
│  │  הימנעות → התאוששות    ●●●●●●●●●●●●  (12 פעמים)        │   │
│  │  נזק → תרומה           ●●●●●●●●      (8 פעמים)         │   │
│  │  סדר → הימנעות         ●●●●●         (5 פעמים)         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ תובנה התנהגותית                                         │   │
│  │ (Behavioral Insight)                                     │   │
│  │                                                          │   │
│  │  "אתה נוטה לבדוק מסלולי התאוששות כשאתה בוחר             │   │
│  │   בהימנעות. זה מצביע על מודעות לצורך במנוחה,            │   │
│  │   אך קושי ליישם אותה בזמן אמת."                         │   │
│  │                                                          │   │
│  │  (You tend to check recovery paths when you choose       │   │
│  │   avoidance. This indicates awareness of the need for    │   │
│  │   rest, but difficulty implementing it in real-time.)    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ נקודות עיוורות אפשריות                                  │   │
│  │ (Potential Blind Spots)                                  │   │
│  │                                                          │   │
│  │  • מעולם לא בדקת מסלול תרומה אחרי החלטת סדר            │   │
│  │  • מעולם לא בדקת מסלול סדר אחרי החלטת התאוששות         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 Implemented Data Model

The backend API `/api/memory/replay-insights/{user_id}` returns:

```javascript
// New aggregation for insights
{
  "user_id": "user-123",
  "summary_period": "last_30_days",
  
  // Path exploration frequency
  "alternative_path_counts": {
    "recovery": 42,
    "order": 28,
    "contribution": 20,
    "harm": 5,
    "avoidance": 5
  },
  
  // Transition pattern frequency
  "transition_patterns": [
    { "from": "avoidance", "to": "recovery", "count": 12 },
    { "from": "harm", "to": "contribution", "count": 8 },
    { "from": "order", "to": "avoidance", "count": 5 }
  ],
  
  // Identified blind spots (never explored)
  "blind_spots": [
    { "from": "order", "to": "contribution" },
    { "from": "recovery", "to": "order" }
  ],
  
  // Generated insights
  "insights": [
    {
      "type": "pattern",
      "hebrew": "אתה נוטה לבדוק מסלולי התאוששות כשאתה בוחר בהימנעות",
      "english": "You tend to check recovery paths when you choose avoidance"
    }
  ],
  
  // Timestamps
  "generated_at": "2026-03-09T12:00:00.000Z"
}
```

### 8.4 Implemented API Endpoint

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/memory/replay-insights/{user_id}` | GET | Get aggregated replay insights |

**Response includes:**
- `total_replays` - Total number of replay explorations
- `alternative_path_counts` - Count per path type (contribution, recovery, order, harm, avoidance)
- `transition_patterns` - List of {from, to, count} patterns sorted by frequency
- `blind_spots` - List of unexplored positive transitions
- `most_replayed_original_tags` - Which decision types get replayed most
- `insights` - Array of Hebrew behavioral insight strings
- `recent_replay_count` - Replays in last 7 days

### 8.5 Future Enhancements

1. **Phase 1: Data Aggregation** ✅ COMPLETE
   - MongoDB aggregation pipeline for pattern counts
   - Pre-computed insights for performance
   - Hebrew insight text generation

2. **Phase 2: UI Component** ✅ COMPLETE
   - Created `ReplayInsightsSummarySection.js`
   - Bar charts for path exploration frequency
   - Transition pattern visualization
   - Blind spots amber-styled section

3. **Phase 3: Smart Insights** ✅ COMPLETE
   - Hebrew insight text generation
   - Blind spot detection algorithm
   - Auto-refresh on new replays

4. **Phase 4: Future - Adaptive Integration** (TODO)
   - Feed replay insights to Adaptive Path Engine
   - Boost paths that user frequently wishes they had chosen
   - Reduce suggestion of paths user rarely explores

---

## Appendix: Hebrew UI Labels Reference

| English | Hebrew | Context |
|---------|--------|---------|
| Decision Replay | הפעלה חוזרת של החלטה | Section title |
| Check alternative path | בדוק מסלול חלופי | Button text |
| Original decision | ההחלטה המקורית | Card label |
| Alternative paths | מסלולים חלופיים אפשריים | Section label |
| Contribution path | מסלול תרומה | Path type |
| Recovery path | מסלול התאוששות | Path type |
| Order path | מסלול סדר | Path type |
| Harm path | מסלול נזק | Path type |
| Avoidance path | מסלול הימנעות | Path type |
| Expected order | סדר צפוי | Metric label |
| Expected collective | קולקטיב צפוי | Metric label |
| Harm pressure | לחץ נזק | Metric label |
| Stability | יציבות | Metric label |
| Balance | איזון | Metric label |
| Insight | תובנה | Section label |

---

**Document Version:** 1.0  
**Author:** E1 Agent  
**Review Status:** Complete
