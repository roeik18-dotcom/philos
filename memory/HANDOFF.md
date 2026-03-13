# Philos Orientation - Complete Project Handoff
## Session End: December 2025

---

# EXECUTIVE SUMMARY

**Philos Orientation** is a Hebrew RTL decision navigation system that:
- Tracks user actions and classifies them into 6 directions
- Uses a theoretical framework with 4 positive directions and balancing paths
- Displays position on a quadrant compass
- Provides theory-based recommendations

**Current State:** Advanced MVP with 5-tab interface, theory integration complete, recommendation engine connected to theoretical framework.

---

# 1. ARCHITECTURE

## Stack
- **Frontend:** React + TailwindCSS + Shadcn/UI
- **Backend:** FastAPI + MongoDB
- **State:** Custom hooks composition pattern

## Core Files

```
/app/frontend/src/
├── pages/PhilosDashboard.js        # Main dashboard (520 lines, 5 tabs)
├── services/
│   ├── recommendationService.js    # CORE: Theory + recommendations (800+ lines)
│   ├── analyticsService.js         # Analytics calculations
│   ├── cloudSync.js                # Cloud operations
│   └── dataService.js              # Caching layer
├── hooks/
│   ├── usePhilosState.js           # Main hook (275 lines, composes others)
│   ├── useDecisionState.js         # Decision evaluation
│   ├── useCloudSync.js             # Cloud sync
│   ├── useAdaptiveScores.js        # Path learning
│   └── useSessionManagement.js     # Stats & sessions
└── components/philos/sections/     # 30+ section components
```

---

# 2. THEORETICAL MODEL

## Four Positive Directions

| Direction | Hebrew | Compass Position (x, y) |
|-----------|--------|------------------------|
| Recovery | התאוששות | (30, 65) lower-left |
| Order | סדר | (30, 25) upper-left |
| Contribution | תרומה | (70, 25) upper-right |
| Exploration | חקירה | (70, 65) lower-right |

## Two Negative Directions

| Direction | Hebrew | Compass Position |
|-----------|--------|-----------------|
| Harm | נזק | (15, 85) far lower-left |
| Avoidance | הימנעות | (50, 90) bottom center |

## Two Tension Axes

```
                סדר (Order) [y=0]
                     ↑
                     |
  אגו (Ego) ←--------+--------→ קולקטיב (Collective)
    [x=0]            |              [x=100]
                     ↓
                כאוס (Chaos) [y=100]
```

**Mapping:**
- `chaos_order`: -100 to +100 → Y: 100 to 0 (inverted)
- `ego_collective`: -100 to +100 → X: 0 to 100

## Balancing Paths (CORE RULES)

```
harm       → recovery      (נזק → התאוששות)
avoidance  → order         (הימנעות → סדר)
isolation  → contribution  (בידוד → תרומה)
rigidity   → exploration   (נוקשות → חקירה)
```

## Positive Reinforcement

```
recovery     → adjacent: order
order        → adjacent: contribution
contribution → adjacent: exploration
exploration  → adjacent: recovery
```

---

# 3. RECOMMENDATION LOGIC

## Location: `/app/frontend/src/services/recommendationService.js`

## Key Functions

```javascript
// Get theory-based recommendation
getTheoryBasedRecommendation(currentDirection) → {
  direction: 'recovery',
  reason: 'theory_balancing',
  explanation: 'פעולות נזק דורשות איזון דרך התאוששות'
}

// Main recommendation calculator
calculateRecommendation({ history, adaptiveScores, ... }) → {
  direction: 'recovery',
  reason: 'theory_balancing',
  strength: 75,
  insight: 'זוהה דפוס נזק...',
  actionSuggestion: 'הפסקה קצרה ומודעת',
  fromTheory: true,
  theoryPath: 'נזק → התאוששות'
}

// Calculate compass position
calculateCompassPosition(history, state) → { x: 30, y: 65, valueTag: 'recovery' }

// Calculate arrow to recommended direction
calculateRecommendedArrow(currentValueTag) → { from, to, direction, explanation }
```

## Priority Order
1. Apply theory balancing paths for negative directions
2. Suggest adjacent positive for positive directions
3. Optional: calibration weights, collective gap adjustments

---

# 4. COMPASS SYSTEM

## Location: `/app/frontend/src/components/philos/sections/OrientationCompassSection.js`

## Features
- Quadrant grid with labeled axes (סדר/כאוס, אגו/קולקטיב)
- Current user position (green dot with pulse animation)
- Recommended direction arrow (dashed green line)
- Trail of recent movements (last 7 days, fading dots)
- Quadrant labels for 4 positive directions

## Position Calculation
```javascript
// Blend theory position (60%) with actual state values (40%)
x = (basePosition.x * 0.6) + (stateX * 0.4)
y = (basePosition.y * 0.6) + (stateY * 0.4)
```

---

# 5. IMPLEMENTED FEATURES

## Navigation (5 Tabs)
```
בית | תובנות | מערכת | תיאוריה | היסטוריה
```

## Theory Tab (`TheorySection.js`)
- 4 directions with descriptions
- 2 tension axes explanation
- Decision logic (3 steps)
- Balancing paths visualization
- Hebrew intro and examples

## Orientation Compass (`OrientationCompassSection.js`)
- Visual compass on Home tab
- User position + recommended arrow
- Movement trail

## Direction History (`DirectionHistorySection.js`)
- Timeframe selector (Today/7 days/All)
- Pattern detection with Hebrew insights
- Distribution chart
- Movement timeline

## Home Navigation (`HomeNavigationSection.js`)
- Action input with helper text
- Follow recommendation button
- Current state display
- Recent decisions

## Onboarding (`OnboardingHint.js`)
- 4-step walkthrough
- Skip button
- localStorage persistence

## Loading States (`LoadingSkeletons.js`)
- 8 reusable skeleton components

---

# 6. DATA STRUCTURES

## Decision Entry
```javascript
{
  id: 'dec_timestamp_random',
  action: 'went for a walk',
  decision: 'Allowed',
  chaos_order: 20,
  ego_collective: 0,
  balance_score: 80,
  value_tag: 'recovery',
  timestamp: 'ISO string',
  followed_recommendation: true,
  recommendation_direction: 'recovery'
}
```

## Recommendation Result
```javascript
{
  direction: 'recovery',
  reason: 'theory_balancing',
  strength: 75,
  insight: 'Hebrew insight text',
  actionSuggestion: 'Hebrew action',
  fromTheory: true,
  theoryPath: 'נזק → התאוששות',
  patternType: 'negative'
}
```

---

# 7. KEY COMPONENT LOCATIONS

| Component | Path | Purpose |
|-----------|------|---------|
| Dashboard | `/app/frontend/src/pages/PhilosDashboard.js` | Main 5-tab interface |
| Theory | `.../sections/TheorySection.js` | Framework explanation |
| Compass | `.../sections/OrientationCompassSection.js` | Visual compass |
| History | `.../sections/DirectionHistorySection.js` | Movement patterns |
| Home | `.../sections/HomeNavigationSection.js` | Action input |
| Recommendations | `/app/frontend/src/services/recommendationService.js` | Core logic |

---

# 8. BACKEND ENDPOINTS

| Endpoint | Purpose |
|----------|---------|
| `POST /api/philos/decisions/{user_id}` | Save decision |
| `GET /api/collective/layer` | Collective data |
| `POST /api/philos/sync` | Cloud sync |
| `GET /api/replay/insights/{user_id}` | Replay insights |

---

# 9. INCOMPLETE WORK

## Orientation Field (Started, Not Finished)
User requested a "Collective Navigation System" with:
1. Collective Orientation Map - distribution across users
2. User vs Collective Position - both on compass
3. Drift Detection - pattern warnings
4. Orientation Momentum - 7-day calculation
5. Insight Layer - meaningful Hebrew insights

**Status:** Backend endpoints added to `server.py` (lines 2019+), frontend component exists at `OrientationFieldSection.js` but needs overwrite.

---

# 10. TEST CREDENTIALS

- **Email:** `newuser@test.com`
- **Password:** `password123`
- **Anonymous:** Auto-generated in localStorage

---

# 11. PREVIEW URL

```
https://trust-ledger-11.preview.emergentagent.com
```

---

# 12. RESUME INSTRUCTIONS

1. Read `/app/memory/PROJECT_STATE_SUMMARY.md` for detailed file structure
2. Read `/app/memory/PRD.md` for product requirements
3. The recommendation service at `/app/frontend/src/services/recommendationService.js` is the single source of truth for theory
4. Complete the Orientation Field feature by updating `OrientationFieldSection.js`
5. Test at the preview URL above
