# Philos Orientation - Product Requirements Document
## Mental Navigation System

**Last Updated:** March 2026  
**Status:** Advanced MVP Complete  
**Preview URL:** https://mental-nav-hub-1.preview.emergentagent.com

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
Completed: System Stabilization (API caching, loading states, error handling)

### Future Priorities
- Refactor `usePhilosState.js` into smaller domain-specific hooks
- Refactor `PhilosDashboard.js` with tabs/accordions for better organization

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
- `PhilosDashboard.js` - Main dashboard with tabs (~500 lines)
- `cloudSync.js` - Cloud sync service with getUserId() (~440 lines)
- `server.py` - FastAPI backend (~2000 lines)
- `sections/` - 33 UI components (including MonthlyOrientationSection)

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

- ✅ **Next Best Direction Feature Completed**
  - NextBestDirectionSection.js - actionable behavioral navigation
  - Uses 6 priority recommendation algorithm:
    1. Negative drift (harm/avoidance >40%) → recommends recovery or order
    2. Collective gap (user below collective >15%) → recommends gap direction  
    3. Replay blind spots → recommends unexplored direction
    4. Positive contribution momentum → recommends contribution
    5. Replay preferences → recommends frequently replayed direction
    6. Balance deficit → recommends lowest positive score direction
  - SVG compass indicator with direction arrow and strength arc
  - Hebrew insight texts with reason footer
  - Action suggestions: "כיוון מומלץ להיום: לסיים משימה פתוחה אחת"
  - Integrates with fetchCollectiveLayer for gap comparison
  - Placed after Continue Previous Session in dashboard layout

- ✅ **Follow Recommendation Action Completed**
  - Button "פעל לפי ההמלצה" in NextBestDirectionSection
  - Clicking prefills action input with recommended action
  - Auto-scrolls to Action Evaluation and focuses input
  - Recommendation indicator: "הפעולה הזו נובעת מהכיוון המומלץ" with direction badge
  - X button to clear recommendation link
  - Metadata saved with decision: recommendation_direction, recommendation_reason, recommendation_strength, followed_recommendation
  - Indicator clears after evaluation

- ✅ **Recommendation Follow-Through Analytics Completed**
  - RecommendationFollowThroughSection.js - tracks recommendation effectiveness
  - Key metrics: follow rate (שיעור מעקב), alignment rate (התאמת תוצאות), most followed direction (הכי נעקב)
  - SVG chart: "התפלגות מעקב לפי כיוון" (distribution by direction)
  - Pattern analysis: strongest (הכי אפקטיבי) and weakest (דורש שיפור) patterns
  - Hebrew insights: "מסלולי התאוששות זוכים לשיעור המעקב הגבוה ביותר", etc.
  - Only shows when user has 2+ followed recommendations
  - Placed after Chain Insights section in dashboard

- ✅ **Recommendation Calibration Completed**
  - RecommendationCalibrationSection.js - self-correcting recommendation weights
  - calculateCalibrationWeights exported and used in NextBestDirectionSection
  - Calibration applied as adjustment layer to base recommendation algorithm
  - Weights bounded between -5 and +5
  - High alignment (>60%) boosts weight, low alignment (<30%) reduces weight
  - SVG visualization of calibrated direction weights (משקלים מכוילים)
  - Shows strongest (הכי מחוזק) and weakest (מופחת) calibrated directions
  - Hebrew insights: "מסלולי התאוששות קיבלו חיזוק בעקבות התאמה גבוהה לתוצאות בפועל"
  - New recommendation reason: "calibration_boost" with "מבוסס על כיול אוטומטי מתוצאות בפועל"
  - "משקל מכויל" indicator shows when calibration affects recommendation
  - Requires 3+ followed recommendations to display

- ✅ **Simplified Home Mode Completed**
  - Reorganized dashboard into 4 tabs: בית (Home), תובנות (Insights), מערכת (System), היסטוריה (History)
  - **Home Tab**: Clean entry screen readable in under 5 seconds
    - מצב היום (Current State): Pattern analysis from recent decisions
    - כיוון מומלץ (Recommended Direction): Direction badge + action suggestion + insight
    - Action input with "פעל לפי ההמלצה" button
    - Decision result display after evaluation
    - Recent history (3 items) with "הצג הכל" link to History tab
  - **Insights Tab**: Chain Insights, Follow-Through Analytics, Weekly/Monthly/Quarterly Reports, Path Engine
  - **System Tab**: Calibration, Collective Mirror/Trajectory/Layer/Trends, Global Field, Value Maps
  - **History Tab**: Decision History, Replay, Tree, Map, Session Library, Comparison
  - HomeNavigationSection.js - simplified home view component
  - All existing sections preserved, only reorganized

- ✅ **Daily Orientation Loop Completed**
  - DailyOrientationLoopSection.js - creates daily return cycle
  - Detects new day by comparing last activity timestamp with current date
  - Shows on new day:
    - "התמצאות יומית" header with "היום מתחיל מחזור חדש של החלטות."
    - **אתמול** (Yesterday): Yesterday's dominant pattern or "לא הייתה פעילות."
    - **היום** (Today): Direction badge + recommended action based on yesterday's pattern
  - "התחל את היום" (Start Day) button saves metadata:
    - day_started, orientation_direction, orientation_pattern_reference, yesterday_count
  - Saves to localStorage (`philos_daily_orientation`) - won't show again same day
  - Pattern → Recommendation mapping: harm→recovery, avoidance→order, contribution→continue

- ✅ **Weekly Orientation Summary Completed**
  - WeeklyOrientationSummarySection.js - creates weekly reset and intention-setting loop
  - Detects new week using year-week format (e.g., 2026-W11)
  - Shows once per new week at top of Home tab:
    - "סיכום שבועי" header with "השבוע החדש מתחיל מתוך הדפוס של השבוע שעבר."
    - **שבוע שעבר** (Last Week): Dominant pattern, strongest positive (↑), strongest negative (↓)
    - **השבוע** (This Week): Direction badge + insight based on last week's patterns
  - "התחל את השבוע" (Start Week) button saves metadata:
    - weekId, week_started, weekly_orientation_direction, weekly_pattern_reference, last_week_decisions
  - Saves to localStorage (`philos_weekly_orientation`) - won't show again same week
  - Purple gradient styling to differentiate from daily (amber)

- ✅ **Monthly Orientation Completed**
  - MonthlyOrientationSection.js - creates monthly reset and direction-setting loop
  - Detects new month using year-month format (e.g., 2026-M03)
  - Shows once per new month at top of Home tab (before weekly/daily):
    - "התמצאות חודשית" header with "החודש החדש מתחיל מתוך הדפוס של החודש שעבר."
    - **Hebrew month name** (e.g., פברואר): Dominant pattern, strongest positive (↑), strongest negative (↓)
    - **החודש** (This Month): Direction badge + insight based on last month's patterns
  - "התחל את החודש" (Start Month) button saves metadata:
    - monthId, month_started, monthly_orientation_direction, monthly_pattern_reference, last_month_decisions
  - Saves to localStorage (`philos_monthly_orientation`) - won't show again same month
  - Teal/Cyan gradient styling to differentiate from weekly (purple) and daily (amber)
  - Orientation hierarchy: Monthly → Weekly → Daily → Home Navigation

- ✅ **System Stabilization Pass Completed**
  - Integrated dataService.js centralized caching layer for all collective API calls
  - Cache TTL: 30 seconds for collective layer, 60 seconds for trends
  - Promise deduplication prevents duplicate simultaneous API calls
  - Components updated to use caching: CollectiveLayerSection, CollectiveTrendsSection, GlobalFieldSection, CollectiveMirrorSection, CollectiveTrajectorySection, WeeklyBehavioralReportSection
  - Added proper loading skeleton states to all collective sections
  - Added Hebrew error messages for API failures
  - Fixed bug in CollectiveMirrorSection (missing API_URL definition)
  - usePhilosState.js now uses fetchReplayInsights from dataService

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

**Product State:** Advanced MVP Complete - System Stabilized
