# Philos Orientation - Product Requirements Document
## Mental Navigation System

**Last Updated:** March 2026  
**Status:** Advanced MVP Complete  
**Preview URL:** https://philos-orient.preview.emergentagent.com

## Current System Status

### Implemented Systems
- **Decision Layer**: Quick Decision, Templates, Daily Prompt
- **Behavioral Analysis**: Chain Insights, Weekly Report, Monthly Report
- **Replay Engine**: Decision Replay, Replay Insights, Replay Adaptive Effect
- **Learning System**: Adaptive scoring from replay patterns
- **User Continuity**: Persistent anonymous user ID, Continue Previous Session
- **Collective Layer**: Collective Mirror, Collective Trajectory

### Architecture Flow
```
Decision → Chain analysis → Weekly aggregation → Replay simulation 
→ Adaptive learning → Collective comparison → Collective trajectory
```

### Next Phase
System Stabilization (performance, loading states, API optimization, error handling)

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

### Phase 16: Persistent Anonymous User ID ✅
- [x] getUserId() function in cloudSync.js uses crypto.randomUUID()
- [x] User ID stored in localStorage on first visit
- [x] User ID reused across page reloads
- [x] All APIs use persistent user ID: decisions, chains, replay, insights, weekly reports
- [x] App.js initializes user ID early on mount
- [x] Components (usePhilosState, ReplayInsightsSummary, WeeklyBehavioralReport) use getUserId()

### Phase 17: Continue Previous Session Prompt ✅
- [x] ContinuePreviousSessionSection component with Hebrew RTL
- [x] Detects returning users with existing history
- [x] Shows last decision text, value tag, relative timestamp
- [x] Shows dominant pattern if available
- [x] Stats badges (total decisions, today decisions)
- [x] "המשך מכאן" button scrolls to action input and focuses it
- [x] Hebrew messages: "המערכת זיהתה שכבר התחלת תהליך קודם", "ניתן להמשיך מאותה נקודה בדיוק"
- [x] Chain indicator if user has decision chains
- [x] Conditional rendering only for users with history

### Phase 18: Collective Mirror ✅
- [x] CollectiveMirrorSection component with Hebrew RTL
- [x] Fetches collective layer API data
- [x] Compares user metrics vs collective: recovery, harm_pressure, order_drift, contribution, replay_exploration
- [x] SVG comparison bars showing "אתה vs ממוצע קולקטיבי"
- [x] Hebrew insights: "התאוששות אצלך גבוהה מהממוצע הקולקטיבי", "לחץ הנזק אצלך השבוע נמוך מהממוצע"
- [x] Stats display: user decisions count, total users
- [x] Color-coded insights (positive=emerald, warning=amber, neutral=gray)
- [x] Footer showing total collective decisions and users

### Phase 19: Collective Trajectory ✅
- [x] CollectiveTrajectorySection component with Hebrew RTL
- [x] Calculates weekly user metrics from history
- [x] Compares user trend vs collective over time
- [x] SVG line chart showing metric trajectories (multi-week view)
- [x] Single-week fallback view with current vs collective comparison
- [x] Trajectory indicators: מתקרב לממוצע (converging), מעל ומתרחק (diverging above), מתחת ומתרחק (diverging below)
- [x] Hebrew insights: "אתה מתקרב בהדרגה למגמת ההתאוששות הקולקטיבית", "תרומתך נעה מעל הממוצע הקולקטיבי לאורך זמן"
- [x] Color-coded trajectory cards and insights

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
- `PhilosDashboard.js` - Main dashboard (~390 lines)
- `cloudSync.js` - Cloud sync service with getUserId() (~440 lines)
- `server.py` - FastAPI backend (~2000 lines)
- `sections/` - 26 UI components (including CollectiveTrajectorySection)

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

- ✅ Implemented Persistent Anonymous User ID
  - getUserId() in cloudSync.js generates UUID once using crypto.randomUUID()
  - User ID stored in localStorage (philos_user_id)
  - User ID persists across page reloads and browser sessions
  - All APIs now use persistent user ID: decisions, chains, replay, insights
  - Updated usePhilosState.js, ReplayInsightsSummarySection, WeeklyBehavioralReportSection
  - App.js initializes user ID early on mount

- ✅ Implemented Continue Previous Session Prompt
  - ContinuePreviousSessionSection.js component with Hebrew RTL
  - Detects returning users with existing history
  - Shows last decision text, value tag ("התאוששות"), relative timestamp ("לפני רגע")
  - Dominant pattern indicator, chain indicator
  - Stats badges (total decisions, today decisions)
  - "המשך מכאן" button scrolls to action input and focuses it
  - Hebrew messages for continuity awareness

- ✅ Implemented Collective Mirror
  - CollectiveMirrorSection.js comparing user vs collective metrics
  - SVG comparison chart with bars for: התאוששות, לחץ נזק, מגמת סדר, תרומה קולקטיבית, חקירת מסלולים
  - Hebrew insights generation based on comparison
  - Color-coded insight cards (positive=emerald, warning=amber, neutral=gray)
  - Stats showing user decisions and total collective users

- ✅ Implemented Collective Trajectory
  - CollectiveTrajectorySection.js showing movement over time
  - Weekly metrics calculation from history
  - SVG line chart for multi-week trajectories
  - Single-week fallback view comparing current vs collective
  - Trajectory indicators: converging, diverging above/below
  - Hebrew insights: "אתה מתקרב בהדרגה למגמת ההתאוששות הקולקטיבית"

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

**Product State:** Advanced MVP Complete - Ready for Stabilization
