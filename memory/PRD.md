# Philos Orientation - Mental Navigation System

## Product Overview
A client-side decision engine and dashboard that provides real-time decision analysis and mental navigation. Features Hebrew RTL interface with tabbed navigation (Home, Insights, System, History).

## Original Problem Statement
Build a sophisticated single-page tool for decision analysis, behavioral tracking, and self-orientation with cloud sync (MongoDB) and user authentication.

## Core Features
- Decision tracking and evaluation
- Value tagging system (contribution, recovery, order, harm, avoidance)
- Replay insights and counterfactual analysis
- Collective intelligence (user vs. collective comparison)
- Recommendation engine with calibration
- Follow-through analytics
- Daily/Weekly/Monthly orientation loops
- Session management and cloud sync

---

## Refactoring Completed (December 2025)

### Phase 1: Recommendation System Centralization ✅
**Status:** Complete
- Created `/app/frontend/src/services/recommendationService.js`
- Functions: `calculateRecommendation()`, `analyzeCurrentState()`, `calculateCalibrationWeights()`, `calculateCollectiveGap()`, `buildRecommendationMetadata()`
- Shared constants: `valueLabels`, `directionColors`, `actionSuggestions`
- Removed duplicate logic from `HomeNavigationSection.js`
- Updated `NextBestDirectionSection.js` and `RecommendationCalibrationSection.js` to use centralized service

### Phase 2: State Architecture Refactoring ✅
**Status:** Complete
- Split `usePhilosState.js` from **1198 lines to 275 lines** (77% reduction)
- Created 5 domain-specific hooks:
  1. `useDecisionState.js` - Core decision evaluation and state persistence
  2. `useCloudSync.js` - Cloud sync, hydration, multi-device continuity
  3. `useReplayState.js` - Decision replay state and actions
  4. `useAdaptiveScores.js` - Adaptive scores and path learning
  5. `useSessionManagement.js` - Global stats, trend history, session snapshots
- **100% backward API compatibility** maintained

### Phase 3: Analytics Centralization ✅
**Status:** Complete
- Created `/app/frontend/src/services/analyticsService.js`
- Functions: `countValueTags()`, `filterHistoryByDateRange()`, `filterTodayHistory()`, `filterLastWeekHistory()`, `calculateDriftMetrics()`, `identifyDominantPattern()`, `analyzePeriodComparison()`, `analyzeFollowThrough()`
- Shared constants: `valueLabels`, `valueColors`
- Updated `DailyOrientationLoopSection.js` and `MonthlyOrientationSection.js` to use centralized analytics

### Phase 4: Real-User Readiness ✅
**Status:** Complete
- Created `/app/frontend/src/components/philos/OnboardingHint.js`
  - 4-step onboarding overlay for first-time users
  - Skip button (hidden on final step)
  - localStorage persistence
  - Reusable components: `SectionHelperText`, `EmptyState`
- Added helper text below action input for new users
- Improved empty state display ("אין נתונים עדיין")
- Default recommendation (recovery) for users with no history

---

## Architecture

### File Structure
```
/app/frontend/src/
├── components/philos/
│   ├── OnboardingHint.js       # First-time user onboarding
│   └── sections/               # 30+ section components
├── hooks/
│   ├── usePhilosState.js       # Main composing hook (275 lines)
│   ├── useDecisionState.js     # Core decision state
│   ├── useCloudSync.js         # Cloud sync
│   ├── useReplayState.js       # Replay state
│   ├── useAdaptiveScores.js    # Adaptive scores
│   └── useSessionManagement.js # Session management
├── services/
│   ├── recommendationService.js # Centralized recommendations
│   ├── analyticsService.js     # Centralized analytics
│   ├── cloudSync.js            # Cloud sync API
│   └── dataService.js          # Data caching layer
└── pages/
    └── PhilosDashboard.js      # Main dashboard (tabbed UI)
```

### Key Technical Decisions
- **State Management:** Composition pattern with domain-specific hooks
- **Recommendation Logic:** Single source of truth in `recommendationService.js`
- **Analytics:** Centralized calculations in `analyticsService.js`
- **UI:** Tabbed navigation (Home, Insights, System, History)
- **Onboarding:** localStorage-based persistence for first-time user tracking

---

## Testing Status
- **Phase 1 Tests:** 12/12 passed (100%)
- **Phase 2 Tests:** 21/21 passed (100%)
- **Phase 4 Tests:** 10/10 passed (100%)

---

## Backlog

### P1 - High Priority
- [ ] Complete system stabilization pass (loading states, error handling)
- [ ] Add consistent error handling for all API requests

### P2 - Medium Priority
- [ ] Further refactor dashboard tab panel content into separate components
- [ ] Add comprehensive unit tests for services

### P3 - Future Enhancements
- [ ] Enhance Decision Path Engine with LLM integration
- [ ] Add more sophisticated collective intelligence features
- [ ] Implement user feedback loop for recommendation improvement

---

## Credentials for Testing
- **Email:** `newuser@test.com`
- **Password:** `password123`
- **Anonymous:** App automatically creates persistent anonymous user ID

---

## Last Updated
December 10, 2025 - All 4 refactoring phases completed
