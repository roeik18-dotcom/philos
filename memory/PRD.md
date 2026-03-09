# Philos Orientation - Product Requirements Document
## Mental Navigation System

**Last Updated:** March 2026  
**Status:** Stable MVP Complete + Decision Replay Feature  
**Preview URL:** https://decision-engine-47.preview.emergentagent.com

---

## Original Problem Statement

Build a complex, client-side decision engine and dashboard called "Philos Orientation." The application serves as a sophisticated single-page tool for real-time decision analysis and mental navigation.

### Core Requirements (All Completed ✅)
- Interactive decision map to visualize decision states
- Suggestion engine for optimal actions
- Decision history and trajectory tracking
- Personal, Collective, and Global value maps
- Session persistence (localStorage + cloud backend)
- Session Library to browse, load, and delete past sessions
- Value Constellation Map visualization
- Session Comparison Engine
- Weekly Cognitive Report
- Decision Path Engine with path suggestions
- User Authentication for cross-device sync

### User Language & UI
- **User Communication:** English
- **UI Language:** Hebrew (עִבְרִית)
- **Layout:** Right-to-Left (RTL)

---

## Implemented Features

### Phase 1: Core Engine ✅
- [x] Event Zero state (physical_capacity, chaos_order, ego_collective, gap_type)
- [x] Action evaluation with decision outcomes
- [x] Value tagging system (contribution, recovery, order, harm, avoidance)
- [x] Balance score calculation
- [x] Suggested vector toward optimal zone

### Phase 2: Decision Path Engine ✅
- [x] 3 suggested action paths generation
- [x] Deterministic algorithm with value preferences
- [x] Predicted metrics display
- [x] Best path highlighting ("מומלץ")
- [x] Risky path marking ("מסוכן")

### Phase 3: Path Learning Layer ✅
- [x] Path selection tracking
- [x] Predicted vs actual comparison
- [x] Match quality assessment
- [x] Hebrew insights generation

### Phase 4: Adaptive Path Engine ✅
- [x] Learning history storage
- [x] Adaptive scoring rules
- [x] Score boosts and penalties
- [x] Decision Path Engine integration

### Phase 5: Persistent Memory Layer ✅
- [x] MongoDB cloud storage
- [x] LocalStorage fallback
- [x] Anonymous user_id support
- [x] API endpoints for all data types

### Phase 6: User Authentication ✅
- [x] Email/password registration
- [x] JWT token authentication
- [x] Password hashing (bcrypt)
- [x] Anonymous data migration
- [x] Hebrew RTL auth screen

### Phase 7: Multi-Device Continuity ✅
- [x] Full data hydration on login
- [x] Cross-device sync
- [x] "מסונכרן בין מכשירים" status
- [x] Logout state preservation

### Phase 8: Collective Layer ✅
- [x] Cross-user aggregated analytics
- [x] Value distribution visualization
- [x] Dominant value/direction indicators
- [x] Hebrew insights

### Phase 9: Collective Trends ✅
- [x] Time-based trends (14-day history)
- [x] SVG sparkline visualizations
- [x] Period comparison (7 days vs 7 days)
- [x] Change indicators
- [x] Hebrew trend insights

### Phase 10: Global Field Visualization ✅
- [x] SVG-based living value system map
- [x] Chaos/Order and Ego/Collective axes
- [x] Harm pressure and recovery zones
- [x] Animated direction indicator (pulsing dot)
- [x] Field state assessment (healthy/tense/organized/balanced)
- [x] Hebrew insights based on collective data
- [x] Real-time data from /api/collective/layer

### Phase 11: Data Generation Layer ✅
- [x] Multiple decisions per session (50 max)
- [x] Auto-save every decision to MongoDB
- [x] Decision frequency tracking
- [x] Floating Quick Decision button with templates
- [x] Decision Chains with parent_decision_id
- [x] Decision History Section
- [x] Decision Tree Visualization
- [x] Chain Insights Section
- [x] Weekly Behavioral Report
- [x] Monthly Progress Report
- [x] Quarterly Review Section
- [x] Daily Decision Prompt (rotating questions)

### Phase 12: Decision Replay ✅
- [x] "בדוק מסלול חלופי" button on history items
- [x] DecisionReplaySection component with Hebrew RTL
- [x] Original decision display with value tag and metrics
- [x] 2-3 alternative paths generation using existing path engine
- [x] Predicted metrics (סדר צפוי, קולקטיב צפוי, לחץ נזק, יציבות)
- [x] Balance difference indicators (+/- איזון)
- [x] Hebrew insight text on path selection
- [x] Backend API for replay metadata (POST /api/memory/replay)
- [x] Replay history retrieval (GET /api/memory/replays/{user_id})
- [x] Replay pattern analysis (pattern_counts aggregation)

### Phase 13: Replay Insights Summary ✅
- [x] ReplayInsightsSummarySection component with Hebrew RTL
- [x] Backend API for aggregated insights (GET /api/memory/replay-insights/{user_id})
- [x] Bar chart visualization of most explored alternative paths
- [x] Transition pattern analysis (from → to with counts)
- [x] Blind spots detection (unexplored positive transitions)
- [x] Hebrew behavioral insights generation (up to 4 insights)
- [x] Summary stats display (total replays, patterns, blind spots)
- [x] Auto-refresh when new replays are added

### Phase 14: Replay Adaptive Effect ✅
- [x] applyReplayInsightsToScores() function in usePhilosState
- [x] Boost frequently explored positive alternatives (contribution, recovery, order)
- [x] Penalize harmful paths users never explore (harm, avoidance)
- [x] ReplayAdaptiveEffectSection component with Hebrew RTL
- [x] Boosted directions display with green bars and boost values
- [x] Penalized directions display with red bars and penalty values
- [x] Hebrew insight texts ("מסלולי תרומה קיבלו חיזוק...", "מסלולי נזק מקבלים כעת הפחתת משקל...")
- [x] Score summary grid with highlighting for boosted/penalized values
- [x] Conditional rendering when adjustments exist
- [x] Auto-update when new replays are added

### Phase 15: Weekly Report Replay Integration ✅
- [x] WeeklyBehavioralReportSection fetches replay insights
- [x] Calculate replayComparison data (mostExploredAlt, missedPositive, avoidedRisky, gapAnalysis)
- [x] SVG visual comparison chart (actual vs replay patterns)
- [x] Stats grid showing: הכי נבדק (most explored), הוחמץ (missed), נמנע (avoided)
- [x] Gap analysis section with Hebrew explanations
- [x] Hebrew replay insights ("השבוע נבדקו שוב ושוב מסלולי...")
- [x] Conditional rendering when replayCount > 0
- [x] Maintains Hebrew RTL layout

---

## Architecture Summary

```
Frontend:  React 18 + Tailwind CSS + Shadcn/UI
Backend:   FastAPI + Motor (async MongoDB)
Database:  MongoDB
Auth:      JWT + bcrypt
State:     Custom Hook (usePhilosState)
```

### Key Files
- `usePhilosState.js` - Central state management (~1180 lines)
- `PhilosDashboard.js` - Main dashboard (~350 lines)
- `cloudSync.js` - Cloud sync service (~400 lines)
- `server.py` - FastAPI backend (~2000 lines)
- `sections/` - 23 UI components (including ReplayAdaptiveEffectSection)

---

## Future Backlog (P2)

1. **Password Reset** - Forgot password functionality
2. **Email Verification** - Verify email on registration
3. **Export/Import** - Session data portability
4. **Advanced Analytics** - Enhanced dashboard views
5. **PWA Support** - Mobile-optimized experience

---

## Changelog

### March 9, 2026
- ✅ Implemented Decision Replay feature
  - Added "בדוק מסלול חלופי" button to Decision History
  - Created DecisionReplaySection.js component
  - Generates 2-3 alternative paths using existing path engine
  - Displays predicted metrics and balance differences
  - Hebrew insight text generation on path selection
  - Backend API: POST /api/memory/replay, GET /api/memory/replays/{user_id}
  - MongoDB collection: philos_replays

- ✅ Implemented Replay Insights Summary feature
  - Created ReplayInsightsSummarySection.js component
  - Bar chart visualization of most explored alternative paths
  - Transition pattern analysis (from → to with counts)
  - Blind spots detection (unexplored positive transitions)
  - Hebrew behavioral insights generation (4 numbered insights)
  - Summary stats display (total replays, patterns, blind spots)
  - Backend API: GET /api/memory/replay-insights/{user_id}
  - Auto-refresh when new replays are added

- ✅ Implemented Replay Adaptive Effect feature
  - Created applyReplayInsightsToScores() function in usePhilosState
  - Boosts frequently explored positive alternatives (contribution +8 max, recovery, order)
  - Penalizes harmful paths never explored (harm -4, avoidance -3)
  - Created ReplayAdaptiveEffectSection.js component
  - Displays boosted directions with green bars and boost values
  - Displays penalized directions with red bars and penalty values
  - Hebrew insights: "מסלולי תרומה קיבלו חיזוק...", "מסלולי נזק מקבלים כעת הפחתת משקל..."
  - Score summary grid with emerald/red highlighting
  - Auto-updates when new replays are added

- ✅ Integrated Replay Insights into Weekly Behavioral Report
  - WeeklyBehavioralReportSection fetches replay insights via API
  - Added replayComparison calculation (mostExploredAlt, missedPositive, avoidedRisky, gapAnalysis)
  - SVG visual comparison chart showing actual vs replay patterns
  - Stats grid: הכי נבדק (most explored), הוחמץ (missed), נמנע (avoided)
  - Gap analysis section with Hebrew explanations
  - Hebrew insights: "השבוע נבדקו שוב ושוב מסלולי...", "נראה פער עקבי..."
  - Conditional rendering when replayCount > 0

### March 8, 2026
- ✅ Implemented Decision Path Engine
- ✅ Implemented Path Learning Layer
- ✅ Implemented Adaptive Path Engine
- ✅ Implemented Persistent Memory Layer
- ✅ Implemented User Authentication
- ✅ Refactored state management to usePhilosState hook
- ✅ Implemented Multi-Device Continuity
- ✅ Implemented Collective Layer Phase 1
- ✅ Implemented Collective Layer Phase 2 (Trends)
- ✅ Implemented Global Field Visualization
- ✅ Implemented Data Generation Layer (auto-save, frequency tracking, quick input)
- ✅ Created PROJECT_SNAPSHOT.md

---

**Product State:** STABLE MVP - All core features + Replay System Complete
