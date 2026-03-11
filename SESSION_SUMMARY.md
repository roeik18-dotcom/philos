# SESSION SUMMARY

## Project Status: MVP COMPLETE

---

## 1. Full System Overview

**Philos Orientation** is a decision navigation system that helps individuals evaluate possible actions and understand their impact on a collective value field. The system learns from decisions and visualizes how human choices shape a global moral landscape.

### Purpose
- Evaluate decision paths
- Learn from outcomes
- Aggregate human decisions into a collective value field
- Turn chained decisions into visible behavioral trajectories

### Core Dimensions
Every decision is evaluated across four dimensions:
- **Physical Capacity**: Energy level (0-100)
- **Chaos ↔ Order**: Structure preference (-100 to +100)
- **Ego ↔ Collective**: Self vs group focus (-100 to +100)
- **Gap Type**: Current challenge area (energy, meaning, connection, purpose)

### Value Tags
- תרומה (Contribution) - Helping others
- התאוששות (Recovery) - Self-care and rest
- סדר (Order) - Organization and structure
- נזק (Harm) - Negative impact
- הימנעות (Avoidance) - Avoiding action

---

## 2. All Implemented Modules

### Phase 1-5: Core Decision Engine ✅
- Daily orientation state tracking
- Action evaluation with outcome prediction
- Decision map visualization (SVG)
- Personal value map
- Collective value map
- Orientation field display
- Global value field
- Global trend tracking

### Phase 6: Session Management ✅
- Session persistence (localStorage + MongoDB)
- Session library for browsing past sessions
- Session comparison engine
- Session export (PNG share cards)
- Weekly summary generation

### Phase 7: Learning System ✅
- Decision Path Engine (3 suggested action paths)
- Path Learning Layer (predicted vs actual comparison)
- Adaptive Path Engine (learns from prediction accuracy)

### Phase 8: User System ✅
- JWT authentication (register/login/logout)
- Multi-device continuity
- Anonymous user support
- Data migration on first login

### Phase 9: Collective Layer ✅
- Anonymized cross-user data aggregation
- Collective trends (14-day history)
- Period comparison (7 days vs 7 days)

### Phase 10: Global Visualization ✅
- SVG-based living value system map
- Chaos/Order and Ego/Collective axes
- Harm pressure and recovery zones
- Animated direction indicator

### Phase 11: Data Generation Layer ✅
- Multiple decisions per session (50 max)
- Auto-save every decision to MongoDB
- Decision frequency tracking (total, daily, weekly)
- Floating Quick Decision button (FAB)
- Decision Templates (5 types)
- Decision Chains (parent_decision_id linking)
- Decision History Section
- Decision Tree Visualization
- Chain Insights Section
- Weekly Behavioral Report
- Monthly Progress Report
- Quarterly Review
- Daily Decision Prompt (rotating questions)

---

## 3. Backend Architecture

### File Structure
```
/app/backend/
├── server.py              # FastAPI application (all routes)
├── requirements.txt       # Python dependencies
└── .env                   # MONGO_URL, DB_NAME
```

### API Endpoints

#### Authentication (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT token |

#### User Data (`/api/user`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/data` | Get authenticated user data |
| GET | `/api/user/full-data/{id}` | Get full user data by ID |
| POST | `/api/user/full-sync/{id}` | Sync all user data |

#### Memory/Decisions (`/api/memory`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/memory/decision` | Save decision with auto-tracking |
| GET | `/api/memory/stats/{user_id}` | Get decision frequency stats |
| GET | `/api/memory/{id}` | Get memory data |
| POST | `/api/memory/path-selection` | Save path selection |
| POST | `/api/memory/path-learning` | Save learning result |

#### Sessions (`/api/philos/sessions`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/philos/sessions/{id}` | Get user sessions |
| POST | `/api/philos/sessions/save` | Save session snapshot |

#### Collective (`/api/collective`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/collective/layer` | Get collective layer data |
| GET | `/api/collective/trends` | Get collective trends |

#### Sync (`/api/philos/sync`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/philos/sync` | Cloud sync |
| POST | `/api/philos/sync/{id}` | Sync by user ID |

### Technologies
- **FastAPI** - Web framework
- **Motor** - Async MongoDB driver
- **Passlib** - Password hashing (bcrypt)
- **python-jose** - JWT handling

---

## 4. Frontend Architecture

### File Structure
```
/app/frontend/src/
├── App.js                      # Auth routing and state
├── index.js                    # Entry point
├── components/
│   ├── ui/                     # Shadcn/UI components
│   └── philos/
│       ├── AuthScreen.js       # Login/Register UI
│       ├── QuickDecisionButton.js  # Floating FAB with templates
│       ├── DecisionMap.js      # SVG decision visualization
│       ├── HistoryList.js      # Decision history list
│       └── sections/           # 26 dashboard section components
│           ├── index.js        # Exports all sections
│           ├── DailyDecisionPromptSection.js
│           ├── DailyOrientationSection.js
│           ├── ActionEvaluationSection.js
│           ├── DecisionMapSection.js
│           ├── DecisionHistorySection.js
│           ├── DecisionTreeSection.js
│           ├── ChainInsightsSection.js
│           ├── WeeklyBehavioralReportSection.js
│           ├── MonthlyProgressReportSection.js
│           ├── QuarterlyReviewSection.js
│           ├── DecisionPathEngineSection.js
│           ├── PathLearningSection.js
│           ├── AdaptiveLearningSection.js
│           ├── CollectiveLayerSection.js
│           ├── CollectiveTrendsSection.js
│           ├── GlobalFieldSection.js
│           └── ... (26 total)
├── hooks/
│   └── usePhilosState.js       # CENTRALIZED STATE MANAGEMENT
├── pages/
│   └── PhilosDashboard.js      # Main dashboard container
└── services/
    └── cloudSync.js            # All API service calls
```

### Key File: usePhilosState.js
Central hook containing:
- All useState hooks (~25 state variables)
- All useEffect hooks for persistence
- Core functions: evaluateAction, handlePathSelection, etc.
- Cloud sync logic
- Authentication integration

### Technologies
- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Shadcn/UI** - Component library
- **html-to-image** - Share card export

---

## 5. Data Collections and Schemas

### users
```javascript
{
  "_id": ObjectId,
  "email": String,
  "password_hash": String,
  "created_at": ISODate,
  "last_login_at": ISODate
}
```

### philos_decisions
```javascript
{
  "_id": ObjectId,
  "id": String (UUID),
  "user_id": String,
  "action": String,
  "decision": String ("Allowed" | "Blocked"),
  "chaos_order": Number (-100 to 100),
  "ego_collective": Number (-100 to 100),
  "balance_score": Number (0 to 100),
  "value_tag": String ("contribution" | "recovery" | "order" | "harm" | "avoidance"),
  "parent_decision_id": String | null,
  "template_type": String | null ("personal" | "social" | "work" | "emotional" | "ethical"),
  "session_id": String | null,
  "time": String ("HH:MM"),
  "date": String ("YYYY-MM-DD"),
  "week": String ("YYYY-MM-DD" week start),
  "timestamp": ISODate
}
```

### philos_user_stats
```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "total_decisions": Number,
  "daily": {
    "YYYY-MM-DD": Number
  },
  "weekly": {
    "YYYY-MM-DD": Number
  },
  "last_decision_at": ISODate,
  "created_at": ISODate
}
```

### philos_sessions
```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "session_data": Object,
  "timestamp": ISODate,
  "name": String,
  "summary": {
    "total_decisions": Number,
    "dominant_value": String,
    "balance_trend": String
  }
}
```

### philos_path_selections
```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "path_data": {
    "path_id": String,
    "path_name": String,
    "predicted_outcome": Object,
    "state_at_selection": Object
  },
  "timestamp": ISODate
}
```

### philos_path_learning_results
```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "learning_data": {
    "selected_path": Object,
    "actual_outcome": Object,
    "predicted_outcome": Object
  },
  "match_quality": String ("excellent" | "good" | "partial" | "poor"),
  "timestamp": ISODate
}
```

---

## 6. Decision Path Engine

### Purpose
Generate 3 suggested action paths based on current state.

### Path Generation Logic
```javascript
// Paths are generated deterministically based on:
// - Current physical_capacity
// - Current gap_type
// - Current chaos_order / ego_collective position

const paths = [
  {
    id: 'recovery',
    name: 'מסלול התאוששות',
    description: 'פעולה לשיקום אנרגיה',
    predicted_outcome: {
      chaos_order: currentState.chaos_order - 10,
      ego_collective: currentState.ego_collective - 5,
      value_tag: 'recovery'
    }
  },
  {
    id: 'contribution',
    name: 'מסלול תרומה',
    description: 'פעולה לטובת הקולקטיב',
    predicted_outcome: {
      chaos_order: currentState.chaos_order + 5,
      ego_collective: currentState.ego_collective + 15,
      value_tag: 'contribution'
    }
  },
  {
    id: 'order',
    name: 'מסלול סדר',
    description: 'פעולה ליצירת מבנה',
    predicted_outcome: {
      chaos_order: currentState.chaos_order + 20,
      ego_collective: currentState.ego_collective,
      value_tag: 'order'
    }
  }
];
```

### Path Selection Flow
1. User views suggested paths
2. User selects a path
3. Selection saved to `philos_path_selections`
4. User performs action
5. Actual outcome compared to predicted
6. Learning result saved to `philos_path_learning_results`

---

## 7. Decision Chains System

### Purpose
Link follow-up decisions to create behavioral trajectories.

### Data Structure
```javascript
// Each decision can reference a parent:
{
  "id": "dec_123",
  "action": "יצאתי להליכה",
  "parent_decision_id": "dec_122",  // Links to parent
  // ... other fields
}
```

### Chain Building Algorithm
```javascript
// Build tree from flat array:
const nodeMap = {};
history.forEach(item => {
  nodeMap[item.id] = { ...item, children: [] };
});

const roots = [];
history.forEach(item => {
  if (item.parent_decision_id && nodeMap[item.parent_decision_id]) {
    nodeMap[item.parent_decision_id].children.push(nodeMap[item.id]);
  } else {
    roots.push(nodeMap[item.id]);
  }
});
```

### UI Components
- **DecisionHistorySection**: Shows "הוסף המשך" button on each item
- **DecisionTreeSection**: Visualizes chains as branching tree
- Parent indicator in ActionEvaluationSection

---

## 8. Chain Insights Logic

### Detection Algorithms

#### Recovery Chain (negative → positive)
```javascript
const startsNegative = ['harm', 'avoidance'].includes(firstValue);
const endsPositive = ['contribution', 'recovery', 'order'].includes(lastValue);
if (startsNegative && endsPositive) {
  // Recovery chain detected
}
```

#### Harm Chain (positive → negative)
```javascript
const startsPositive = ['contribution', 'recovery', 'order'].includes(firstValue);
const endsNegative = ['harm', 'avoidance'].includes(lastValue);
if (startsPositive && endsNegative) {
  // Harm chain detected
}
```

#### Correction Pattern (mid-chain repair)
```javascript
for (let i = 1; i < values.length - 1; i++) {
  if (negativeValues.includes(values[i]) && positiveValues.includes(values[i + 1])) {
    // Correction found at position i
  }
}
```

#### Growth Chain (all positive)
```javascript
const allPositive = values.every(v => positiveValues.includes(v));
if (allPositive && chain.length >= 2) {
  // Growth chain
}
```

#### Warning Chain (all negative)
```javascript
const allNegative = values.every(v => negativeValues.includes(v));
if (allNegative && chain.length >= 2) {
  // Warning chain
}
```

#### Repeated Patterns
```javascript
const patterns = {};
chains.forEach(chain => {
  const pattern = chain.map(n => n.value_tag).join('→');
  patterns[pattern] = (patterns[pattern] || 0) + 1;
});
// Count patterns appearing 2+ times
```

---

## 9. Weekly Behavioral Report

### Aggregation Period
- Last 7 days from current date

### Metrics Tracked
- recovery chains count
- harm chains count
- correction chains count
- growth chains count
- warning chains count
- total decisions
- total chains

### Visualizations
- SVG horizontal bar chart
- Stacked distribution bar
- Dominant pattern highlight
- Strongest movement cards

### Hebrew Insights Generated
- "השבוע בלטו יותר שרשראות התאוששות"
- "יש עלייה בדפוסי נזק - שים לב"
- "נמצאו X תיקונים באמצע מסלולים"
- "יש רצף של החלטות חיוביות - המשך כך!"

---

## 10. Monthly Progress Report

### Aggregation Period
- Last 4 weeks (28 days)

### Metrics Tracked
- Weekly breakdown of all chain types
- Trend calculation (first half vs second half)
- Strongest shifts (positive and negative)
- Dominant monthly pattern

### Visualizations
- SVG stacked bar chart (4 weeks)
- Trend indicator boxes (+/- per category)
- Overall progress bar
- Movement highlight cards

### Hebrew Insights Generated
- "בחודש האחרון ניכרת עלייה בשרשראות התאוששות"
- "נראה ירידה עקבית בדפוסי נזק"
- "דפוסי תיקון נעשו תכופים יותר לאורך החודש"
- "מגמה כללית חיובית החודש 📈"

---

## 11. Collective Layer Analytics

### Data Aggregation
- Anonymous aggregation from all users
- Excludes individual identifiers
- Calculates distribution percentages

### Metrics
- Value distribution (% per value_tag)
- Average chaos_order position
- Average ego_collective position
- Total collective decisions
- Active users count

### Trend Analysis
- 14-day historical data
- SVG sparkline visualizations
- Period comparison (7d vs 7d)
- Change indicators (up/down arrows)

### Global Field Visualization
- SVG map with axes:
  - X: Chaos ↔ Order
  - Y: Ego ↔ Collective
- Harm zone (bottom-left, red)
- Recovery zone (top-right, blue)
- Animated direction indicator (pulsing dot)
- Field state assessment

---

## 12. Daily Decision Prompt

### Component: DailyDecisionPromptSection

### Rotating Questions (7 prompts)
```javascript
const dailyPrompts = [
  { question: 'מה הייתה החלטה קטנה שקיבלת היום?', placeholder: 'החלטתי ל...' },
  { question: 'איך הגבת למצב לא צפוי היום?', placeholder: 'כשקרה... הגבתי ב...' },
  { question: 'הייתה תגובה רגשית שהיית רוצה לנתח?', placeholder: 'הרגשתי... ואז...' },
  { question: 'איזו החלטה השפיעה על היום שלך?', placeholder: 'ההחלטה ל... השפיעה...' },
  { question: 'מה עשית כדי להתקדם היום?', placeholder: 'עשיתי צעד קדימה כש...' },
  { question: 'האם נמנעת ממשהו היום?', placeholder: 'נמנעתי מ...' },
  { question: 'איך עזרת למישהו היום?', placeholder: 'עזרתי ל... ב...' }
];
```

### Selection Logic
```javascript
const dayOfYear = Math.floor((now - yearStart) / (1000 * 60 * 60 * 24));
const todayPrompt = dailyPrompts[dayOfYear % dailyPrompts.length];
```

### Behavior
- Shows today's decision count badge
- "הוסף החלטה" button scrolls to input
- Pre-fills placeholder text
- Auto-focuses input field

---

## 13. Quick Decision Panel

### Component: QuickDecisionButton

### Features
- Floating action button (FAB) in bottom-left
- Expands to full input panel
- Template selector
- Quick suggestion buttons
- Stats display (today/total)

### UI Elements
```
┌─────────────────────────┐
│ החלטה מהירה             │ ← Header
│ מה עשית או מתכנן לעשות? │
├─────────────────────────┤
│ [Template Buttons]      │ ← 5 templates
├─────────────────────────┤
│ [Textarea Input]        │ ← Action input
├─────────────────────────┤
│ [Quick Suggestions]     │ ← הליכה, מנוחה, עזרה, עבודה
├─────────────────────────┤
│ [הוסף החלטה]            │ ← Submit button
├─────────────────────────┤
│ היום: 3  |  סה״כ: 47    │ ← Stats footer
└─────────────────────────┘
```

---

## 14. Decision Templates

### 5 Template Types
```javascript
const DECISION_TEMPLATES = [
  { id: 'personal', label: 'אישי', icon: '👤', prompt: 'מהי הפעולה שאני שוקל כרגע?' },
  { id: 'social', label: 'חברתי', icon: '👥', prompt: 'איך בחרתי להגיב באינטראקציה החברתית?' },
  { id: 'work', label: 'עבודה', icon: '💼', prompt: 'מה עשיתי כדי להתקדם במשימה?' },
  { id: 'emotional', label: 'רגשי', icon: '💭', prompt: 'איך הגבתי לרגש שהרגשתי?' },
  { id: 'ethical', label: 'אתי', icon: '⚖️', prompt: 'מה הייתה ההחלטה המוסרית שקיבלתי?' }
];
```

### Behavior
- Clicking template highlights it
- Pre-fills input with guiding question
- Template type saved with decision
- Can deselect by clicking again

---

## 15. Data Generation Layer

### Purpose
Increase volume and quality of decision data feeding the collective layer.

### Components
1. **Multiple decisions per session** - History holds 50 items (up from 20)
2. **Auto-save** - Every decision saved to MongoDB immediately
3. **Frequency tracking** - Total, daily, weekly counts per user
4. **Quick Decision FAB** - Easy entry point for decisions
5. **Decision Templates** - Guided prompts for different contexts
6. **Decision Chains** - Parent-child linking for trajectories
7. **Daily Prompt** - Rotating questions to encourage daily input

### Data Flow
```
User Input → evaluateAction() → setHistory() → saveDecision() → MongoDB
                                     ↓
                              Update philos_user_stats
                                     ↓
                              Feed into collective layer
```

### Stats Endpoint Response
```javascript
{
  "success": true,
  "user_id": "user_abc123",
  "total_decisions": 47,
  "today_decisions": 3,
  "week_decisions": 12,
  "last_decision_at": "2025-12-15T14:30:00Z"
}
```

---

## Test Credentials

- **Email**: newuser@test.com
- **Password**: password123

---

## Preview URL

https://daily-orientation.preview.emergentagent.com

---

## Document References

| File | Purpose |
|------|---------|
| `/app/memory/PRD.md` | Product requirements document |
| `/app/SESSION_STATE.md` | Quick state reference |
| `/app/RELEASE_CHECKPOINT.md` | Release documentation |
| `/app/PRODUCT_OVERVIEW.md` | Product vision |
| `/app/PROJECT_SNAPSHOT.md` | System snapshot |

---

## Summary

**Philos Orientation MVP** is a complete decision navigation system featuring:

- ✅ Full decision evaluation engine
- ✅ Chain-based trajectory tracking
- ✅ Multi-level behavioral analytics (weekly/monthly/quarterly)
- ✅ Collective intelligence layer
- ✅ User authentication with multi-device sync
- ✅ Hebrew RTL interface
- ✅ Cloud persistence with MongoDB
- ✅ Data generation optimization

**Total Section Components**: 26
**Total API Endpoints**: ~15
**Total MongoDB Collections**: 6

---

**Document Created**: December 2025
**Project Status**: MVP COMPLETE
