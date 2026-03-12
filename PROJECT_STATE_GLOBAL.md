# Philos Orientation - Development State Summary
## Context Preservation Document

**Generated:** March 8, 2026  
**Purpose:** Development continuity across context resets  
**Preview URL:** https://decision-engine-lab.preview.emergentagent.com

---

## CORE SYSTEM

### Decision Engine ✅
- Event Zero state: `physical_capacity`, `chaos_order`, `ego_collective`, `gap_type`
- Action evaluation: Allowed/Blocked outcomes
- Value tagging: `contribution`, `recovery`, `order`, `harm`, `avoidance`
- Balance score calculation
- Suggested vector toward optimal zone
- **Location:** `usePhilosState.js` → `evaluateAction()`, `getValueTag()`

### Decision Path Engine ✅
- Generates 3 suggested action paths
- Deterministic algorithm (prefers: order, recovery, contribution)
- Predicted metrics: order_drift, collective_drift, harm_pressure, recovery_stability
- Best path: "מומלץ" badge | Risky path: "מסוכן" badge
- Integrates adaptive scores for ranking
- **Location:** `DecisionPathEngineSection.js`

### Path Learning Layer ✅
- Tracks selected paths on "בחר מסלול זה" click
- Compares predicted vs actual outcomes
- Match quality: high/medium/low
- Hebrew insights generation
- **Location:** `PathLearningSection.js`

### Adaptive Path Engine ✅
- Stores learning history (last 50 entries)
- Adaptive scoring rules:
  - Boost: better recovery, lower harm, improved order, high match
  - Penalty: increased harm, low match, outcomes toward harm/avoidance
- Score range: -20 to +20 per value type
- **Location:** `AdaptiveLearningSection.js`, `usePhilosState.js`

---

## MEMORY

### Persistent Memory Layer ✅
- **Backend:** MongoDB collections via Motor async driver
- **Frontend:** LocalStorage fallback for offline usage
- **Sync:** Automatic cloud sync on data changes (5s debounce)

### Collections:
```
philos_sessions        # User session data (history, global_stats, trend_history)
philos_saved_sessions  # Session library
philos_decisions       # Individual decision records
philos_path_selections # Path selection records
philos_path_learning   # Learning results (predicted vs actual)
philos_adaptive_scores # Calculated adaptive scores per user
```

### Learning History
- Stores last 50 learning entries per user
- Fields: predicted/actual value_tag, drifts, pressures, match_quality
- Auto-synced to cloud on evaluation

### Adaptive Scores
- Per-user score for each value type
- Recalculated from full learning history
- Cloud-persisted with localStorage cache

---

## IDENTITY

### User Authentication ✅
- **Registration:** Email + password
- **Login:** JWT token (30-day expiration)
- **Password:** bcrypt hashing via passlib
- **Hebrew RTL:** Auth screen fully localized

### Anonymous → User Migration
- On first login, migrates existing anonymous data
- Updates all collections: sessions, decisions, path_selections, path_learning, adaptive_scores
- Preserves user_id consistency
- **Endpoint:** `POST /api/auth/migrate-data`

---

## CONTINUITY

### Multi-Device Sync ✅
- Full data hydration on login via `GET /api/user/full-data/{user_id}`
- Syncs: history, globalStats, trendHistory, learningHistory, adaptiveScores
- Status badge: "מסונכרן בין מכשירים" when synced
- **Location:** `usePhilosState.js` → `hydrateFromCloud()`

### Cloud + Local Fallback
- Primary: MongoDB cloud storage
- Fallback: localStorage for offline/anonymous usage
- Merge strategy: Timestamp-based deduplication
- **Location:** `cloudSync.js`

---

## COLLECTIVE

### Collective Layer (Phase 1) ✅
- Cross-user aggregated analytics (anonymized)
- Metrics: total users/decisions, value counts, avg drifts
- Dominant value and direction indicators
- Hebrew insights
- **Endpoint:** `GET /api/collective/layer`
- **Component:** `CollectiveLayerSection.js`

### Collective Trends (Phase 2) ✅
- Time-based trends (14-day history)
- SVG sparkline visualizations (lightweight)
- Period comparison: last 7 days vs previous 7 days
- Change indicators with percentages
- Hebrew trend insights
- **Endpoint:** `GET /api/collective/trends`
- **Component:** `CollectiveTrendsSection.js`

---

## ARCHITECTURE

### Frontend
```
Framework:        React 18
Styling:          Tailwind CSS
UI Components:    Shadcn/UI (from /components/ui/)
Icons:            Lucide React
Image Export:     html-to-image
State Management: Custom Hook (usePhilosState)
Language:         Hebrew RTL throughout
```

### Backend
```
Framework:  FastAPI
Database:   MongoDB (Motor async driver)
Auth:       JWT (python-jose), bcrypt (passlib)
CORS:       Starlette middleware
Logging:    Python logging module
```

### Database
```
MongoDB
├── Users collection (auth)
├── philos_sessions (session data)
├── philos_saved_sessions (library)
├── philos_decisions (individual records)
├── philos_path_selections
├── philos_path_learning
└── philos_adaptive_scores
```

---

## STATE MANAGEMENT

### usePhilosState Hook
**Location:** `/app/frontend/src/hooks/usePhilosState.js` (~830 lines)

**State Variables:**
```javascript
state              // Event Zero: physical_capacity, chaos_order, ego_collective, gap_type
actionText         // Current action input
decisionResult     // Last evaluation result
history            // Decision history (last 20)
globalStats        // Global value counts
trendHistory       // Daily trend snapshots (last 30 days)
selectedPathData   // Currently selected path
learningHistory    // Path learning records (last 50)
adaptiveScores     // Adaptive scoring adjustments
syncStatus         // Cloud sync status
showShareCard      // UI state
```

**Exported Functions:**
```javascript
evaluateAction()           // Evaluate user action
handlePathSelection()      // Handle path selection
resetSession()             // Reset current session
resetGlobalStats()         // Reset global stats
loadSessionFromLibrary()   // Load saved session
performCloudSync()         // Trigger cloud sync
getTrajectoryDirection()   // Get movement direction
exportSession()            // Export session JSON
```

**Exported Utilities:**
```javascript
calculateSuggestedVector() // Calculate optimal zone vector
analyzePersonalMap()       // Analyze personal patterns
getValueTag()              // Determine action value tag
```

---

## KEY API GROUPS

### /api/auth
```
POST /api/auth/register           # Register new user
POST /api/auth/login              # Login user → JWT token
POST /api/auth/logout             # Logout (client-side)
GET  /api/auth/me                 # Get current user info
POST /api/auth/migrate-data       # Migrate anonymous data
```

### /api/memory
```
POST /api/memory/decision         # Save decision record
POST /api/memory/path-selection   # Save path selection
POST /api/memory/path-learning    # Save learning result
GET  /api/memory/{user_id}        # Get memory data
POST /api/memory/sync             # Sync memory data
```

### /api/user
```
GET  /api/user/full-data/{user_id}  # Get ALL user data
POST /api/user/full-sync/{user_id}  # Full sync with merge
```

### /api/collective
```
GET /api/collective/layer         # Aggregated cross-user analytics
GET /api/collective/trends        # Time-based collective trends
```

### /api/sync (Legacy)
```
POST /api/sync                    # Sync session data
GET  /api/sync/{user_id}          # Get session data
```

### /api/philos/sessions
```
POST   /api/philos/sessions/{user_id}               # Save to library
GET    /api/philos/sessions/{user_id}               # Get saved sessions
DELETE /api/philos/sessions/{user_id}/{session_id}  # Delete session
```

---

## CURRENT DEVELOPMENT TASK

### Global Field Visualization (IN PROGRESS)

**Goal:** Create a single high-level visual field representing the collective value system as one living map.

**Requirements:**
- Visualize dominant value clusters
- Show collective direction (order ↔ chaos, ego ↔ collective)
- Display harm pressure zones
- Display recovery zones
- Show order vs chaos field tendency
- Use lightweight SVG only (no heavy chart libraries)
- Add Hebrew insight text
- Keep RTL layout

**File Created:**
`/app/frontend/src/components/philos/sections/GlobalFieldSection.js`

**Status:** Component created, needs:
1. Export added to `sections/index.js`
2. Import and render in `PhilosDashboard.js`
3. Restart frontend
4. Screenshot verification

**Uses Endpoint:** `GET /api/collective/layer` (already exists)

---

## FILE REFERENCE

### Core Files
```
/app/frontend/src/hooks/usePhilosState.js      # State management (~830 lines)
/app/frontend/src/pages/PhilosDashboard.js     # Main dashboard (~270 lines)
/app/frontend/src/services/cloudSync.js        # Cloud sync (~400 lines)
/app/backend/server.py                         # FastAPI backend (~1650 lines)
```

### Section Components (19 total)
```
/app/frontend/src/components/philos/sections/
├── index.js
├── DailyOrientationSection.js
├── ActionEvaluationSection.js
├── DecisionMapSection.js
├── DecisionPathEngineSection.js
├── PathLearningSection.js
├── AdaptiveLearningSection.js
├── PersonalMapSection.js
├── CollectiveValueMapSection.js
├── OrientationFieldSection.js
├── GlobalValueFieldSection.js
├── GlobalTrendSection.js
├── SessionSummarySection.js
├── SessionLibrarySection.js
├── SessionComparisonSection.js
├── ValueConstellationSection.js
├── WeeklySummarySection.js
├── CollectiveLayerSection.js
├── CollectiveTrendsSection.js
└── GlobalFieldSection.js          # NEW - needs integration
```

### Auth Component
```
/app/frontend/src/components/auth/AuthScreen.js
```

### Documentation
```
/app/PROJECT_SNAPSHOT.md           # Full system snapshot
/app/PROJECT_STATE_GLOBAL.md       # This file
/app/memory/PRD.md                 # Product requirements
```

---

## ENVIRONMENT

### Frontend (.env)
```
REACT_APP_BACKEND_URL=https://decision-engine-lab.preview.emergentagent.com
```

### Backend (.env)
```
MONGO_URL=<MongoDB connection string>
DB_NAME=<Database name>
JWT_SECRET_KEY=<Secret key>
CORS_ORIGINS=*
```

### Services
```bash
# Check status
sudo supervisorctl status

# Restart
sudo supervisorctl restart backend frontend

# Logs
tail -f /var/log/supervisor/backend.*.log
tail -f /var/log/supervisor/frontend.*.log
```

---

## NEXT STEPS (After Context Reset)

1. **Complete Global Field Visualization:**
   - Add export to `sections/index.js`
   - Import in `PhilosDashboard.js`
   - Place after Collective Trends section
   - Restart frontend
   - Verify with screenshot

2. **Future Backlog:**
   - Password Reset functionality
   - Email Verification
   - Export/Import session data
   - Advanced analytics dashboard

---

**Document Status:** COMPLETE  
**Product Status:** STABLE MVP  
**Current Task:** Global Field Visualization (integration pending)
