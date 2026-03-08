# Philos Orientation - Product Requirements Document

## Project State: SAVED (March 7, 2026)

## Original Problem Statement
Create a mindfulness/decision-making app that evolved into the **Philos Orientation** system - a comprehensive mental navigation and decision engine with visual dashboard.

## Current State - COMPLETE

### All Completed Features ✅

| Feature | Status | Description |
|---------|--------|-------------|
| Decision Engine | ✅ | Action evaluation, value tagging, balance scoring |
| Personal Map | ✅ | Direction indicators, top values, value graph |
| Collective Value Map | ✅ | Session value distribution, collective patterns |
| Orientation Field | ✅ | Order/collective drift, harm pressure, recovery stability |
| Global Value Field | ✅ | Cross-session analytics with dominant value cluster |
| Global Trend Over Time | ✅ | Sparkline charts, trend insights, auto-save snapshots |
| Cloud Sync | ✅ | MongoDB backend, auto-sync, offline fallback |
| Session Library | ✅ | Save/load/delete sessions, browsable cards |

### Backend API Endpoints

```
Base URL: https://wisdom-dashboard.preview.emergentagent.com/api

# Health Check
GET  /                           → {"message": "Hello World"}

# Cloud Sync
POST /philos/sync                → Sync local data with cloud
GET  /philos/sync/{user_id}      → Get cloud data for user

# Session Library
POST /philos/sessions/save?user_id={id}           → Save session
GET  /philos/sessions/{user_id}                    → List all sessions
GET  /philos/sessions/{user_id}/{session_id}       → Get session details
DELETE /philos/sessions/{user_id}/{session_id}     → Delete session
```

### Database Collections (MongoDB)
- `philos_sessions` - User session data (history, globalStats, trendHistory)
- `philos_saved_sessions` - Session Library entries

## Current State (March 2026)

### What's Implemented ✅

#### Core Decision Engine
- Action evaluation with value tagging
- Decision computation (Allowed/Blocked)
- Balance Score calculation: `100 - (|chaos_order| + |ego_collective|)`
- Trajectory tracking and projection
- Smart fallbacks based on gap_type

#### Dashboard UI (`/app/frontend/src/pages/PhilosDashboard.js`)
- **Header**: Title, tagline, session counter, Reset Session button
- **State Sliders**: Gap type, Physical Capacity, Chaos/Order, Ego/Collective
- **Emotional State**: Calm/Stressed/Confused buttons that adjust chaos_order
- **Micro Actions**: Quick energy recovery buttons (+10 energy)
- **Quick Actions**: Pre-defined action buttons
- **Action Evaluation**: Text input + Evaluate Decision button
- **Decision Display**: Status, projection values, Value Tag badge
- **Decision Explanation**: Reasoning for the decision
- **Suggested Actions**: Vector suggestion when outside optimal zone
- **Orientation Status Panel**: Order, Collective, Energy, Balance Score
- **Suggested Stabilizing Actions**: Appears when balance < 30
- **Recover Energy**: Buttons that increase physical_capacity
- **Daily Loop**: Visual workflow guide
- **Decision Map**: 2D visualization with animated dot, trajectory path, suggestion arrow
- **Decision History**: Last 20 decisions with time, action, status
- **Session Summary**: Actions count, Balance Score, Trajectory, Energy status
- **Personal Map**: Direction indicators, Top Values, Decision Timeline, Value Graph, Your Pattern
- **Orientation Field**: Order Drift, Collective Drift, Harm Pressure, Recovery Stability
- **Collective Value Map**: Value distribution circles, Collective Pattern summary
- **Share Card**: Modal with downloadable PNG card
- **Export Session**: Download JSON data

#### Value Tag System
- **contribution**: help, support, friend, give, assist, share, care
- **recovery**: walk, breathe, stretch, water, rest, sleep, pause
- **harm**: angry, attack, insult, shout, hurt, revenge, fight
- **order**: organize, clean, plan, focus, work, structure, sort
- **avoidance**: ignore, avoid, delay, scroll, escape, postpone

#### Data Persistence
- localStorage saving/loading
- Session state preservation across page reloads
- Reset Session functionality with confirmation
- Cloud sync with MongoDB backend
- Automatic sync on app load and data changes
- Manual sync button
- Offline fallback to localStorage

#### Visualizations
- Decision Map with animated dot movement
- Trajectory path connecting previous decisions
- Suggestion vector arrow toward optimal zone
- Optimal zone glow when balanced
- Value Graph with clustered nodes by value_tag
- Mini timeline bars for decision history
- Clustered circles for value distribution

### Technical Stack
- **Frontend**: React 18, Tailwind CSS
- **Visualization**: SVG-based graphics
- **Persistence**: localStorage
- **Export**: html-to-image for PNG, JSON download

### Architecture
```
/app/frontend/src/
├── pages/
│   └── PhilosDashboard.js  # Main app (~912 lines - refactored)
├── components/
│   └── philos/
│       ├── DecisionMap.js  # 2D map visualization
│       └── sections/       # Extracted section components
│           ├── index.js
│           ├── DailyOrientationSection.js
│           ├── ActionEvaluationSection.js
│           ├── DecisionMapSection.js
│           ├── PersonalMapSection.js
│           ├── CollectiveValueMapSection.js
│           ├── OrientationFieldSection.js
│           ├── GlobalValueFieldSection.js
│           ├── GlobalTrendSection.js
│           ├── SessionSummarySection.js
│           ├── SessionLibrarySection.js
│           ├── ValueConstellationSection.js
│           ├── SessionComparisonSection.js
│           └── WeeklySummarySection.js
└── App.js
```

## Key Metrics

### Balance Score
- Formula: `100 - (|chaos_order| + |ego_collective|)`
- Green (≥70): Balanced
- Yellow (40-69): Unstable
- Red (<40): Conflict

### Orientation Field Metrics
- **Order Drift**: (order + recovery) - (harm + avoidance)
- **Collective Drift**: contribution - harm
- **Harm Pressure**: harm / total decisions
- **Recovery Stability**: recovery / total decisions

### Global Value Field Metrics (Cross-Session)
- **Global Order Drift**: Aggregated (order + recovery) - (harm + avoidance) from all sessions
- **Global Collective Drift**: Aggregated contribution - harm from all sessions
- **Harm Pressure Long Term**: Global harm count / total global decisions
- **Recovery Stability Long Term**: Global recovery count / total global decisions
- **Dominant Value Cluster**: Most frequent value tag across all sessions

### Global Trend Metrics (Time Series)
- **Order Drift Trend**: Direction of order drift change over sessions
- **Collective Drift Trend**: Direction of social orientation over time
- **Harm Pressure Trend**: Whether harm actions are increasing or decreasing
- **Recovery Stability Trend**: Consistency of recovery actions over time

### Optimal Zone
- Order: 20-60
- Collective: 10-50

## Completed Features (This Session)

1. ✅ Fixed blank page bug
2. ✅ Simplified Action Evaluation flow
3. ✅ Added Decision Explanation
4. ✅ Added Decision History (20 items)
5. ✅ Added Trajectory Map with animated dots
6. ✅ Added Vector Suggestion Engine
7. ✅ Added Vector Arrow on Decision Map
8. ✅ Added Orientation Status Panel
9. ✅ Added Reset Session button
10. ✅ Added Quick Demo Actions
11. ✅ Added Emotional State buttons
12. ✅ Added Micro Actions for energy recovery
13. ✅ Added Balance Score with color coding
14. ✅ Added Suggested Stabilizing Actions
15. ✅ Added Recover Energy section
16. ✅ Added Daily Loop visualization
17. ✅ Updated header with tagline
18. ✅ Added Session Summary
19. ✅ Added Export Session (JSON)
20. ✅ Added Share Card with PNG download
21. ✅ Added Personal Map with Value Graph
22. ✅ Added Collective Value Map
23. ✅ Added Orientation Field metrics
24. ✅ Improved value_tag detection
25. ✅ Added session persistence (localStorage)
26. ✅ Added Global Value Field (cross-session analytics)
    - Global Order Drift: (order + recovery) - (harm + avoidance) across all sessions
    - Global Collective Drift: contribution - harm across all sessions
    - Harm Pressure Long Term: harm / total percentage
    - Recovery Stability Long Term: recovery / total percentage
    - Dominant Value Cluster visualization
    - Global Value Distribution circles
    - Reset global stats button
    - Persisted in localStorage separately from session data
27. ✅ Refactored PhilosDashboard.js into smaller components
    - Reduced main file from 1727 lines to 912 lines
    - Extracted 8 section components:
      - DailyOrientationSection
      - ActionEvaluationSection
      - DecisionMapSection
      - PersonalMapSection
      - CollectiveValueMapSection
      - OrientationFieldSection
      - GlobalValueFieldSection
      - SessionSummarySection
    - All behavior and UI unchanged
28. ✅ Added Global Trend Over Time section
    - Sparkline bar charts for 4 metrics:
      - Order Drift (סחף סדר)
      - Collective Drift (סחף חברתי)
      - Harm Pressure (לחץ נזק)
      - Recovery Stability (יציבות התאוששות)
    - Shows last 10 sessions
    - Trend direction indicators (↑ עולה / ↓ יורד / → יציב)
    - Trend Insight summary box with actionable insights
    - Auto-saves session snapshots every 5 decisions
    - Persisted in localStorage (philos_trend_history)
29. ✅ Implemented Cloud Sync for session data
    - Backend API endpoints for sync (POST /api/philos/sync, GET /api/philos/sync/{user_id})
    - MongoDB storage for persistent data
    - Automatic sync on app load and after data changes (5s debounce)
    - Manual sync button available
    - Merges local and cloud data intelligently
    - Sync status indicator in header (מסונכרן לענן / מסנכרן... / מצב לא מקוון)
    - localStorage remains as fallback cache
    - Syncs: history, globalStats, trendHistory
30. ✅ Built Session Library feature
    - New API endpoints: POST /api/philos/sessions/save, GET /api/philos/sessions/{user_id}, DELETE /api/philos/sessions/{user_id}/{session_id}
    - SessionLibrarySection component with expandable UI
    - Save current session to cloud library
    - Browse saved sessions as cards showing: date, decisions count, dominant value, order drift, collective drift
    - "פתח סשן" (Open Session) button to load saved sessions
    - Delete sessions with confirmation
    - Hebrew RTL layout preserved
31. ✅ Built Value Constellation Map
    - Spatial SVG visualization of value clusters
    - Fixed node positions: order (top), contribution (top-right), recovery (right), avoidance (left), harm (bottom)
    - Node size represents decision count per value
    - Transition lines between nodes showing decision flow
    - Dominant value highlighted with animated glow
    - Hover tooltips with value name, count, percentage
    - Value distribution bar chart
    - Stats: transitions count, dominant value with percentage
32. ✅ Built Session Comparison Engine
    - Select two saved sessions from dropdowns
    - Side-by-side comparison metrics display
    - Visual comparison bars for: decision count, order drift, collective drift, harm pressure, recovery stability
    - Color-coded bars (green for better, blue/red for relative)
    - Dominant value display for each session
    - Auto-generated Hebrew insights (תובנות השוואה)
    - Hebrew RTL layout preserved
33. ✅ Built Weekly Cognitive Report
    - Aggregates last 7 days of trend history
    - Overview stats: total decisions, session count, dominant value
    - Weekly averages: order drift, collective drift, harm pressure, recovery stability
    - Trend indicators for each metric (↑ עולה / ↓ יורד / → יציב)
    - Weekly value distribution bar with counts
    - Auto-generated Hebrew insights (תובנות שבועיות)
    - Shows empty state when no data available

## Backlog / Future Tasks

### P1 - High Priority
- [x] Refactor PhilosDashboard.js into smaller components (DONE)
- [x] Historical trend analysis (DONE - Global Trend section)
- [x] Cloud sync for session data (DONE)
- [ ] User authentication
- [ ] Multi-device support

### P2 - Medium Priority
- [ ] Social features (share with community)
- [ ] Global value map across users
- [ ] Historical trend analysis
- [ ] Weekly/monthly reports

### P3 - Low Priority
- [ ] Mobile app (React Native)
- [ ] Notifications/reminders
- [ ] Integration with calendar
- [ ] AI-powered suggestions

## Preview URL
https://wisdom-dashboard.preview.emergentagent.com

---

## Resume Development Notes

When continuing development, the next priorities are:
1. **User Authentication** - Email/password or Google OAuth for multi-device support
2. **Session Comparison** - Compare two saved sessions side by side
3. **Social Features** - Share sessions with community

### Key Files to Review
- `/app/frontend/src/pages/PhilosDashboard.js` - Main dashboard component
- `/app/frontend/src/services/cloudSync.js` - Cloud sync service
- `/app/backend/server.py` - All API endpoints
- `/app/frontend/src/components/philos/sections/` - All section components

### Language Note
All UI text is in **Hebrew (עִבְרִית)** with RTL orientation. User communication is in English.
