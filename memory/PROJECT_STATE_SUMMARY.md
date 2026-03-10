# Philos Orientation - Project State Summary
## Last Updated: December 2025

---

## 1. ARCHITECTURE OVERVIEW

### Main Modules

```
/app
├── backend/                    # FastAPI + MongoDB
│   └── server.py              # 2000+ lines, all API endpoints
├── frontend/                   # React + TailwindCSS
│   └── src/
│       ├── components/philos/ # All Philos components
│       ├── hooks/             # State management hooks
│       ├── services/          # API and business logic
│       └── pages/             # Main dashboard
└── memory/                    # Project documentation
```

### Services Layer (`/app/frontend/src/services/`)

| File | Purpose |
|------|---------|
| `recommendationService.js` | **CORE** - Theory-based recommendations, compass positions, balancing paths |
| `analyticsService.js` | Centralized analytics calculations, pattern detection |
| `dataService.js` | Caching layer for API calls |
| `cloudSync.js` | Cloud sync, user ID management, decision saving |

### Hooks Layer (`/app/frontend/src/hooks/`)

| File | Purpose | Lines |
|------|---------|-------|
| `usePhilosState.js` | Main composing hook (backward compatible API) | ~275 |
| `useDecisionState.js` | Core decision evaluation, value tagging | ~200 |
| `useCloudSync.js` | Cloud sync, multi-device hydration | ~200 |
| `useReplayState.js` | Decision replay functionality | ~60 |
| `useAdaptiveScores.js` | Path learning, adaptive scoring | ~250 |
| `useSessionManagement.js` | Global stats, trend history, snapshots | ~200 |

### Core Components (`/app/frontend/src/components/philos/sections/`)

**Theory & Navigation:**
- `TheorySection.js` - Theoretical framework explanation
- `OrientationCompassSection.js` - Visual compass with user position
- `DirectionHistorySection.js` - Movement history with pattern detection

**Home Tab:**
- `HomeNavigationSection.js` - Main action input, recommendation display
- `DailyOrientationLoopSection.js` - Daily orientation prompt
- `WeeklyOrientationSummarySection.js` - Weekly summary
- `MonthlyOrientationSection.js` - Monthly orientation

**Insights Tab:**
- `NextBestDirectionSection.js` - Full recommendation engine display
- `DecisionPathEngineSection.js` - Path selection
- `ReplayInsightsSummarySection.js` - Replay analytics

**System Tab:**
- `RecommendationCalibrationSection.js` - Calibration weights
- `RecommendationFollowThroughSection.js` - Follow-through analytics
- `CollectiveMirrorSection.js` - User vs collective comparison
- `CollectiveTrajectorySection.js` - Collective trends

---

## 2. THEORETICAL MODEL

### Four Directions (Positive)

| Direction | Hebrew | Position on Compass | Description |
|-----------|--------|---------------------|-------------|
| Recovery | התאוששות | Lower-left (30, 65) | Stabilization after stress |
| Order | סדר | Upper-left (30, 25) | Structure, organization |
| Contribution | תרומה | Upper-right (70, 25) | Action for others |
| Exploration | חקירה | Lower-right (70, 65) | Openness, flexibility |

### Two Negative Directions

| Direction | Hebrew | Position on Compass | Description |
|-----------|--------|---------------------|-------------|
| Harm | נזק | Far lower-left (15, 85) | Damaging actions |
| Avoidance | הימנעות | Bottom center (50, 90) | Escape, postponement |

### Two Tension Axes

```
                    סדר (Order)
                        ↑
                        |
       אגו (Ego) ←------+------→ קולקטיב (Collective)
                        |
                        ↓
                    כאוס (Chaos)
```

**Axis Mapping:**
- `chaos_order`: -100 (chaos) to +100 (order) → Y axis (inverted: 100 to 0)
- `ego_collective`: -100 (ego) to +100 (collective) → X axis (0 to 100)

### Balancing Path Rules (CORE THEORY)

```javascript
theoryBalancingPaths = {
  harm:      { balancingDirection: 'recovery' },    // נזק → התאוששות
  avoidance: { balancingDirection: 'order' },       // הימנעות → סדר
  isolation: { balancingDirection: 'contribution' }, // בידוד → תרומה
  rigidity:  { balancingDirection: 'exploration' }  // נוקשות → חקירה
}
```

### Positive Reinforcement Rules

```javascript
positiveReinforcement = {
  recovery:     { strengthen: 'recovery', adjacent: 'order' },
  order:        { strengthen: 'order', adjacent: 'contribution' },
  contribution: { strengthen: 'contribution', adjacent: 'exploration' },
  exploration:  { strengthen: 'exploration', adjacent: 'recovery' }
}
```

---

## 3. IMPLEMENTED PRODUCT FEATURES

### Navigation Tabs (5 tabs)

```
בית | תובנות | מערכת | תיאוריה | היסטוריה
Home | Insights | System | Theory | History
```

### Theory Tab Features
- Four directions explanation with descriptions
- Two tension axes explanation
- Decision logic (3 steps): Actions → Patterns → Orientation
- Balancing paths visualization (נזק→התאוששות, etc.)
- Visual quadrant map preview
- Hebrew intro and examples

### Orientation Compass Features
- Quadrant grid with labeled axes
- Current user position (green dot with pulse)
- Recommended direction arrow (dashed)
- Trail of recent movements (last 7 days)
- Legend and empty state
- Position calculated from theory + actual values

### Direction History Features
- Timeframe selector: היום | 7 ימים | הכל
- Mini compass with movement trail
- Pattern detection with Hebrew insights:
  - "אתה נוטה לנוע לכיוון התאוששות"
  - "יש חזרתיות בהימנעות ולאחריה סדר"
- Direction distribution chart
- Movement timeline

### Recommendation Engine
- Theory-based: Uses balancing paths directly
- Returns: direction, reason, strength, insight, actionSuggestion
- Calibration weights from follow-through data
- Collective gap consideration

### Onboarding
- 4-step onboarding overlay for first-time users
- Helper text for empty states
- localStorage persistence

### Loading Skeletons
- `LoadingSkeletons.js` with 8 reusable components
- Integrated in async sections

---

## 4. DATA STRUCTURES

### Decision/Action Entry

```javascript
{
  id: 'dec_1234567890_abc123',
  action: 'went for a walk',
  decision: 'Allowed',
  chaos_order: 20,           // -100 to +100
  ego_collective: 0,         // -100 to +100
  balance_score: 80,         // 0-100
  value_tag: 'recovery',     // One of 6 directions
  parent_decision_id: null,  // For decision chains
  time: '14:30',
  timestamp: '2025-12-10T14:30:00.000Z',
  // Optional recommendation metadata:
  followed_recommendation: true,
  recommendation_direction: 'recovery',
  recommendation_reason: 'theory_balancing',
  recommendation_strength: 75
}
```

### Compass Position

```javascript
compassPositions = {
  recovery:     { x: 30, y: 65, quadrant: 'lower-left' },
  order:        { x: 30, y: 25, quadrant: 'upper-left' },
  contribution: { x: 70, y: 25, quadrant: 'upper-right' },
  exploration:  { x: 70, y: 65, quadrant: 'lower-right' },
  harm:         { x: 15, y: 85, quadrant: 'far-lower-left' },
  avoidance:    { x: 50, y: 90, quadrant: 'bottom-center' }
}
```

### Recommendation Result

```javascript
{
  direction: 'recovery',
  reason: 'theory_balancing',
  strength: 75,
  insight: 'זוהה דפוס נזק. פעולות נזק דורשות איזון דרך התאוששות',
  actionSuggestion: 'הפסקה קצרה ומודעת',
  negativeRatio: 0.4,
  valueCounts: { harm: 3, recovery: 2, ... },
  calibrationApplied: false,
  fromTheory: true,
  theoryPath: 'נזק → התאוששות',
  currentDirection: 'harm',
  patternType: 'negative'
}
```

### Pattern Analysis

```javascript
{
  dominantDirection: 'harm',
  dominantCount: 4,
  dominanceRatio: 0.4,
  patternType: 'negative',  // 'positive', 'negative', 'balanced'
  valueCounts: { harm: 4, avoidance: 2, recovery: 3, order: 1 },
  theoryCategory: 'harm'    // Maps to balancing path lookup
}
```

### Calibration Weights

```javascript
{
  weights: {
    contribution: 3,  // -5 to +5
    recovery: 1,
    order: -2,
    harm: 0,
    avoidance: 0
  },
  hasData: true,
  insights: ['מסלולי תרומה קיבלו חיזוק...'],
  strongestDir: 'contribution',
  weakestDir: 'order'
}
```

---

## 5. FILE STRUCTURE

### Frontend Components

```
/app/frontend/src/components/philos/
├── LoadingSkeletons.js           # Reusable loading skeletons
├── OnboardingHint.js             # First-time user onboarding
├── QuickDecisionButton.js        # Quick decision input
└── sections/
    ├── index.js                  # Exports all sections
    │
    │ # Theory & Navigation
    ├── TheorySection.js          # Theoretical framework
    ├── OrientationCompassSection.js  # Visual compass
    ├── DirectionHistorySection.js    # Movement history
    │
    │ # Home Tab
    ├── HomeNavigationSection.js  # Main action input
    ├── DailyOrientationLoopSection.js
    ├── WeeklyOrientationSummarySection.js
    ├── MonthlyOrientationSection.js
    │
    │ # Insights Tab
    ├── NextBestDirectionSection.js
    ├── DecisionPathEngineSection.js
    ├── PathLearningSection.js
    ├── AdaptiveLearningSection.js
    ├── ReplayInsightsSummarySection.js
    ├── ReplayAdaptiveEffectSection.js
    │
    │ # System Tab
    ├── RecommendationCalibrationSection.js
    ├── RecommendationFollowThroughSection.js
    ├── CollectiveMirrorSection.js
    ├── CollectiveTrajectorySection.js
    ├── GlobalFieldSection.js
    │
    │ # History Tab
    ├── DecisionHistorySection.js
    ├── DecisionTreeSection.js
    ├── ChainInsightsSection.js
    │
    │ # Reports
    ├── WeeklyBehavioralReportSection.js
    ├── MonthlyProgressReportSection.js
    ├── QuarterlyReviewSection.js
    │
    │ # Other
    ├── DecisionReplaySection.js
    ├── ContinuePreviousSessionSection.js
    ├── DailyDecisionPromptSection.js
    └── ... (30+ total sections)
```

### Services

```
/app/frontend/src/services/
├── recommendationService.js   # 800+ lines - CORE theory logic
│   ├── theoryBalancingPaths
│   ├── positiveReinforcement
│   ├── compassPositions
│   ├── getTheoryBasedRecommendation()
│   ├── identifyDominantPattern()
│   ├── calculateCompassPosition()
│   ├── calculateRecommendedArrow()
│   ├── calculateRecommendation()
│   ├── analyzeRecentHistory()
│   ├── calculateCalibrationWeights()
│   └── analyzeCurrentState()
│
├── analyticsService.js        # 350+ lines - Analytics
│   ├── countValueTags()
│   ├── filterHistoryByDateRange()
│   ├── calculateDriftMetrics()
│   ├── identifyDominantPattern()
│   ├── analyzePeriodComparison()
│   └── analyzeFollowThrough()
│
├── dataService.js             # Caching layer
│   ├── fetchCollectiveLayer()
│   ├── fetchReplayInsights()
│   └── Cache management
│
└── cloudSync.js               # Cloud operations
    ├── getUserId()
    ├── saveDecision()
    ├── syncWithCloud()
    ├── getCloudData()
    └── getFullUserData()
```

### Hooks

```
/app/frontend/src/hooks/
├── usePhilosState.js          # Main composing hook
├── useDecisionState.js        # Decision evaluation
├── useCloudSync.js            # Cloud sync
├── useReplayState.js          # Replay functionality
├── useAdaptiveScores.js       # Path learning
└── useSessionManagement.js    # Stats & sessions
```

### Main Page

```
/app/frontend/src/pages/
└── PhilosDashboard.js         # ~520 lines
    ├── Tab navigation (5 tabs)
    ├── Home tab content
    ├── Insights tab content
    ├── System tab content
    ├── Theory tab content
    └── History tab content
```

---

## 6. BACKEND API ENDPOINTS

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/philos/sync` | POST | Cloud sync |
| `/api/philos/cloud` | GET | Get cloud data |
| `/api/philos/decisions/{user_id}` | POST | Save decision |
| `/api/collective/layer` | GET | Collective data |
| `/api/collective/trends` | GET | Collective trends |
| `/api/memory/learning` | POST | Save learning data |
| `/api/memory/replay` | POST | Save replay metadata |
| `/api/replay/insights/{user_id}` | GET | Replay insights |

### New Orientation Field Endpoints (Added but may need file update)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/orientation/field` | GET | Collective field distribution |
| `/api/orientation/user/{user_id}` | GET | User vs collective position |
| `/api/orientation/drift/{user_id}` | GET | Drift detection |

---

## 7. NEXT STEPS (INCOMPLETE)

### Orientation Field System (Started, Not Complete)
The user requested a major "ORIENTATION FIELD" feature to transform Philos into a collective navigation system:

1. **Collective Orientation Map** - Show distribution across all users
2. **User vs Collective Position** - Both dots on compass
3. **Direction Drift Detection** - Pattern detection
4. **Orientation Momentum** - Last 7 days calculation
5. **Insight Layer** - Generate meaningful insights

**Status:** Backend endpoints added to server.py, frontend component exists but may need overwrite.

---

## 8. CREDENTIALS

- **Test User:** `newuser@test.com` / `password123`
- **Anonymous:** Auto-generated persistent ID in localStorage

---

## 9. KEY DESIGN DECISIONS

1. **Theory-First Recommendations** - All recommendations follow the theoretical balancing paths
2. **Compass as Core Visual** - Quadrant grid with axes, not circular
3. **Hebrew RTL** - All UI text in Hebrew, right-to-left layout
4. **Hooks Composition** - Large state hook split into 5 domain-specific hooks
5. **Centralized Services** - recommendationService and analyticsService as single sources of truth
6. **No Feature Creep** - Focus on orientation signals, not action tracking
