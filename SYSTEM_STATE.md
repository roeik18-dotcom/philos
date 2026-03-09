# Philos Orientation - System State Documentation

**Last Updated:** March 9, 2026  
**System Status:** Advanced MVP with Multiple Behavioral Analysis Layers  
**Next Priority:** System Stabilization Pass

---

## Core System Components

### 1. Decision Layer
| Component | File | Description |
|-----------|------|-------------|
| Quick Decision | `QuickDecisionButton.js` | Floating quick-add panel |
| Decision Templates | `QuickDecisionButton.js` | Personal, social, work, emotional, ethical templates |
| Daily Decision Prompt | `DailyDecisionPromptSection.js` | Rotating daily questions to encourage engagement |
| Action Evaluation | `ActionEvaluationSection.js` | Main decision input and evaluation |

### 2. Behavior Analysis Layer
| Component | File | Description |
|-----------|------|-------------|
| Chain Insights | `ChainInsightsSection.js` | Analysis of decision chains |
| Weekly Report | `WeeklyBehavioralReportSection.js` | Weekly behavioral patterns + replay integration |
| Monthly Report | `MonthlyProgressReportSection.js` | Monthly progress analysis |
| Quarterly Review | `QuarterlyReviewSection.js` | Long-term trend analysis |

### 3. Replay Simulation Engine
| Component | File | Description |
|-----------|------|-------------|
| Decision Replay | `DecisionReplaySection.js` | Counterfactual path exploration |
| Replay Insights | `ReplayInsightsSummarySection.js` | Aggregated replay pattern analysis |
| Replay Adaptive Effect | `ReplayAdaptiveEffectSection.js` | Shows how replays affect scoring |

### 4. Adaptive Learning Layer
| Component | Location | Description |
|-----------|----------|-------------|
| applyReplayInsightsToScores() | `usePhilosState.js` | Adjusts scores based on replay patterns |
| Path Learning | `PathLearningSection.js` | Compares predicted vs actual outcomes |
| Adaptive Learning | `AdaptiveLearningSection.js` | Shows adaptive score adjustments |

### 5. User Continuity Layer
| Component | File | Description |
|-----------|------|-------------|
| Persistent User ID | `cloudSync.js` | UUID stored in localStorage |
| Continue Session | `ContinuePreviousSessionSection.js` | Welcome back prompt for returning users |

### 6. Collective Intelligence Layer
| Component | File | Description |
|-----------|------|-------------|
| Collective Mirror | `CollectiveMirrorSection.js` | User vs collective comparison |
| Collective Trajectory | `CollectiveTrajectorySection.js` | User movement vs collective trends |
| Collective Layer | `CollectiveLayerSection.js` | Cross-user analytics |
| Global Field | `GlobalFieldSection.js` | Collective value system visualization |

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER DECISION                                   │
│                              │                                          │
│                              ▼                                          │
│                    ┌─────────────────┐                                  │
│                    │  Decision Input  │                                  │
│                    │  (Templates)     │                                  │
│                    └────────┬────────┘                                  │
│                              │                                          │
│              ┌───────────────┼───────────────┐                          │
│              ▼               ▼               ▼                          │
│     ┌────────────┐   ┌────────────┐   ┌────────────┐                   │
│     │   Chain    │   │   Weekly   │   │   Replay   │                   │
│     │  Analysis  │   │ Aggregation│   │ Simulation │                   │
│     └──────┬─────┘   └──────┬─────┘   └──────┬─────┘                   │
│              │               │               │                          │
│              └───────────────┼───────────────┘                          │
│                              ▼                                          │
│                    ┌─────────────────┐                                  │
│                    │ Replay Learning │                                  │
│                    │   (Patterns)    │                                  │
│                    └────────┬────────┘                                  │
│                              │                                          │
│                              ▼                                          │
│                    ┌─────────────────┐                                  │
│                    │ Adaptive Score  │                                  │
│                    │   Adjustment    │                                  │
│                    └────────┬────────┘                                  │
│                              │                                          │
│              ┌───────────────┼───────────────┐                          │
│              ▼               ▼               ▼                          │
│     ┌────────────┐   ┌────────────┐   ┌────────────┐                   │
│     │ Collective │   │ Collective │   │   Hebrew   │                   │
│     │   Mirror   │   │ Trajectory │   │  Insights  │                   │
│     └────────────┘   └────────────┘   └────────────┘                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Files Reference

### Frontend Components (26 sections)
```
/app/frontend/src/components/philos/sections/
├── ActionEvaluationSection.js
├── AdaptiveLearningSection.js
├── ChainInsightsSection.js
├── CollectiveLayerSection.js
├── CollectiveMirrorSection.js         # NEW
├── CollectiveTrajectorySection.js     # NEW
├── CollectiveTrendsSection.js
├── CollectiveValueMapSection.js
├── ContinuePreviousSessionSection.js  # NEW
├── DailyDecisionPromptSection.js
├── DailyOrientationSection.js
├── DecisionHistorySection.js
├── DecisionMapSection.js
├── DecisionPathEngineSection.js
├── DecisionReplaySection.js           # NEW
├── DecisionTreeSection.js
├── GlobalFieldSection.js
├── GlobalTrendSection.js
├── GlobalValueFieldSection.js
├── MonthlyProgressReportSection.js
├── OrientationFieldSection.js
├── PathLearningSection.js
├── PersonalMapSection.js
├── QuarterlyReviewSection.js
├── ReplayAdaptiveEffectSection.js     # NEW
├── ReplayInsightsSummarySection.js    # NEW
├── SessionComparisonSection.js
├── SessionLibrarySection.js
├── SessionSummarySection.js
├── ValueConstellationSection.js
├── WeeklyBehavioralReportSection.js   # UPDATED
└── WeeklySummarySection.js
```

### State Management
```
/app/frontend/src/hooks/usePhilosState.js  (~1180 lines)
- Central state management
- calculateAdaptiveScores()
- applyReplayInsightsToScores()
- saveReplayMetadata()
- handleReplayDecision()
```

### Services
```
/app/frontend/src/services/
├── cloudSync.js     # getUserId(), cloud sync, decision saving
└── dataService.js   # NEW - Centralized caching (in progress)
```

### Backend
```
/app/backend/server.py  (~2000 lines)
- FastAPI application
- MongoDB integration
- All API endpoints
```

---

## Backend API Endpoints

### Replay System
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/memory/replay` | Save replay metadata |
| GET | `/api/memory/replays/{user_id}` | Get replay history |
| GET | `/api/memory/replay-insights/{user_id}` | Get aggregated replay insights |

### Collective System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/collective/layer` | Get collective layer data |
| GET | `/api/collective/trends` | Get collective trends |

### Decision System
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/memory/decision` | Save decision |
| GET | `/api/memory/decisions/{user_id}` | Get user decisions |
| GET | `/api/memory/stats/{user_id}` | Get user stats |

---

## MongoDB Collections

| Collection | Purpose |
|------------|---------|
| `users` | User authentication |
| `philos_decisions` | Decision records with chains |
| `philos_user_stats` | Decision frequency stats |
| `philos_replays` | Replay metadata |
| `philos_sessions` | Session snapshots |
| `philos_paths` | Path selections |
| `philos_learning` | Learning history |

---

## Hebrew UI Labels Reference

| English | Hebrew | Context |
|---------|--------|---------|
| Decision Replay | הפעלה חוזרת של החלטה | Section title |
| Continue from Previous Session | המשך מהמפגש הקודם | Welcome back |
| Collective Mirror | מראה קולקטיבית | Comparison section |
| Collective Trajectory | מסלול קולקטיבי | Movement section |
| Replay Insights Summary | סיכום תובנות הפעלה חוזרת | Analysis section |
| Replay Adaptive Effect | השפעת הפעלה חוזרת על מסלולים | Adaptive section |
| Weekly Behavioral Report | דו"ח התנהגותי שבועי | Report section |
| Boosted directions | כיוונים מחוזקים | Adaptive display |
| Penalized directions | כיוונים מוחלשים | Adaptive display |

---

## Next Priority: System Stabilization

### Tasks
1. **Audit all sections** - Ensure proper conditional rendering
2. **Optimize data fetching** - Use centralized `dataService.js` for caching
3. **Add loading states** - For all async components
4. **Error handling** - Graceful degradation for all API calls
5. **RTL consistency** - Verify all sections
6. **SVG performance** - Review chart rendering

### Known Issues to Address
- Multiple components calling `/api/collective/layer` independently
- Missing loading states in some sections
- No centralized error handling

---

## Test Credentials

| Field | Value |
|-------|-------|
| Email | `newuser@test.com` |
| Password | `password123` |

---

## Documentation Files

| File | Purpose |
|------|---------|
| `/app/memory/PRD.md` | Product requirements and changelog |
| `/app/REPLAY_SYSTEM.md` | Replay system architecture |
| `/app/SYSTEM_STATE.md` | This file - current system state |
| `/app/test_reports/` | Test iteration reports |

---

**Document Version:** 1.0  
**Author:** E1 Agent  
**Status:** Active Development
