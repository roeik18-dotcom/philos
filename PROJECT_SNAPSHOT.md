# Philos Orientation - System Snapshot
## Mental Navigation System
**Snapshot Date:** March 8, 2026  
**Version:** 1.0.0 Stable MVP  
**Preview URL:** https://orient-global.preview.emergentagent.com

---

## SYSTEM OVERVIEW

### Core Philosophy
Philos Orientation is a sophisticated client-side decision engine and dashboard for real-time decision analysis and mental navigation. The application helps users evaluate actions, track decision patterns, and navigate toward optimal mental states through a value-based framework.

### Feature Modules

#### 1. Decision Engine (Core)
- Event Zero state management (physical_capacity, chaos_order, ego_collective, gap_type)
- Action evaluation with decision outcomes (Allowed/Blocked)
- Value tagging system: `contribution`, `recovery`, `order`, `harm`, `avoidance`
- Balance score calculation
- Suggested vector toward optimal zone

#### 2. Decision Path Engine
- Generates 3 suggested action paths based on current state
- Deterministic algorithm preferring: order, recovery, contribution
- Penalizes: harm, avoidance
- Predicted metrics: order_drift, collective_drift, harm_pressure, recovery_stability
- Best path highlighting with "מומלץ" (Recommended) badge
- Risky path marking with "מסוכן" (Risky) badge

#### 3. Path Learning Layer
- Tracks selected paths when user clicks "בחר מסלול זה"
- Compares predicted vs actual outcomes after evaluation
- Displays: predicted outcome, actual outcome, match quality (high/medium/low)
- Generates Hebrew insights based on comparison

#### 4. Adaptive Path Engine
- Stores learning history for selected paths
- Builds adaptive scoring rules from historical performance
- Boosts: better-than-predicted recovery, lower harm pressure, improved order drift
- Penalizes: increased harm, low match quality, outcomes toward harm/avoidance
- Updates Decision Path Engine scoring with adaptive adjustments

#### 5. Persistent Memory Layer
- Cloud storage via MongoDB for:
  - Sessions, Decisions, Path selections
  - Path learning results, Adaptive scores
- LocalStorage fallback for offline usage
- Anonymous user_id for unauthenticated users
- User-specific data for authenticated users

#### 6. User Authentication
- Email/password registration and login
- JWT tokens with 30-day expiration
- Password hashing with bcrypt
- Anonymous data migration on first login
- Hebrew RTL auth screen

#### 7. Multi-Device Continuity
- Full user data hydration on login
- Syncs: history, globalStats, trendHistory, learningHistory, adaptiveScores
- "מסונכרן בין מכשירים" status badge for authenticated users
- Preserves anonymous local fallback on logout

#### 8. Collective Layer (Phase 1)
- Cross-user aggregated analytics (anonymized)
- Total users and decisions count
- Value distribution visualization (clustered circles)
- Metrics: avg order/collective drift, harm pressure, recovery stability
- Dominant value and direction indicators
- Hebrew insights

#### 9. Collective Trends (Phase 2)
- Time-based collective trends (14-day history)
- SVG sparkline visualizations
- Period comparison (last 7 days vs previous 7 days)
- Bar chart comparing value distributions
- Change indicators with percentage
- Hebrew trend insights

---

## ARCHITECTURE

### Frontend Stack
```
Framework:     React 18
Styling:       Tailwind CSS
UI Components: Shadcn/UI
Icons:         Lucide React
Image Export:  html-to-image
State:         Custom Hook (usePhilosState)
```

### Backend Stack
```
Framework:     FastAPI
Database:      MongoDB (Motor async driver)
Auth:          JWT (python-jose), bcrypt (passlib)
CORS:          Starlette middleware
```

### Database
```
MongoDB
└── Collections managed via Motor async driver
└── All _id fields excluded from API responses
└── Anonymous user_id generation for unauthenticated users
```

---

## CORE FILES

### Frontend

#### `/app/frontend/src/hooks/usePhilosState.js` (~830 lines)
Central state management hook containing:
- All state declarations (state, history, globalStats, learningHistory, etc.)
- Cloud sync functions
- Evaluation logic
- Path selection handling
- Learning data persistence
- Utility functions (calculateSuggestedVector, analyzePersonalMap, getValueTag)

#### `/app/frontend/src/pages/PhilosDashboard.js` (~270 lines)
Main dashboard component:
- Uses usePhilosState hook
- Renders all section components
- Auth UI integration
- Sync status display

#### `/app/frontend/src/services/cloudSync.js` (~400 lines)
Cloud synchronization service:
- User ID management
- Session sync (syncWithCloud, getCloudData)
- Memory sync (savePathSelection, savePathLearning, getMemoryData)
- Multi-device sync (getFullUserData, fullSyncUserData)

#### `/app/frontend/src/components/auth/AuthScreen.js` (~230 lines)
Authentication screen:
- Login/Register tabs
- Hebrew RTL layout
- Form validation
- Anonymous data migration

#### `/app/frontend/src/components/philos/sections/` (19 components)
```
├── index.js                      # Exports all sections
├── DailyOrientationSection.js    # Event Zero sliders
├── ActionEvaluationSection.js    # Action input & results
├── DecisionMapSection.js         # Visual decision map
├── DecisionPathEngineSection.js  # 3 suggested paths
├── PathLearningSection.js        # Predicted vs actual comparison
├── AdaptiveLearningSection.js    # Adaptive scores display
├── PersonalMapSection.js         # Personal value map
├── CollectiveValueMapSection.js  # User's collective map
├── OrientationFieldSection.js    # Orientation status
├── GlobalValueFieldSection.js    # Global value stats
├── GlobalTrendSection.js         # Personal trend sparklines
├── SessionSummarySection.js      # Session summary
├── SessionLibrarySection.js      # Saved sessions list
├── SessionComparisonSection.js   # Compare two sessions
├── ValueConstellationSection.js  # SVG constellation map
├── WeeklySummarySection.js       # Weekly cognitive report
├── CollectiveLayerSection.js     # Cross-user analytics
└── CollectiveTrendsSection.js    # Time-based trends
```

### Backend

#### `/app/backend/server.py` (~1650 lines)
FastAPI server containing:
- MongoDB connection setup
- JWT configuration and helpers
- All API endpoints
- Pydantic models for request/response

---

## API ENDPOINTS

### Health & Status
```
GET  /api/                              # Health check
GET  /api/status                        # Status checks list
POST /api/status                        # Create status check
```

### Authentication
```
POST /api/auth/register                 # Register new user
POST /api/auth/login                    # Login user
POST /api/auth/logout                   # Logout (client-side)
GET  /api/auth/me                       # Get current user info
POST /api/auth/migrate-data             # Migrate anonymous data to user
```

### Philos Session Sync
```
POST /api/sync                          # Sync session data
GET  /api/sync/{user_id}                # Get session data
POST /api/philos/sessions/{user_id}     # Save session to library
GET  /api/philos/sessions/{user_id}     # Get saved sessions
DELETE /api/philos/sessions/{user_id}/{session_id}  # Delete session
```

### Persistent Memory
```
POST /api/memory/decision               # Save decision record
POST /api/memory/path-selection         # Save path selection
POST /api/memory/path-learning          # Save learning result
GET  /api/memory/{user_id}              # Get memory data
POST /api/memory/sync                   # Sync memory data
```

### Multi-Device Continuity
```
GET  /api/user/full-data/{user_id}      # Get ALL user data
POST /api/user/full-sync/{user_id}      # Full sync with merge
```

### Collective Layer
```
GET  /api/collective/layer              # Aggregated cross-user analytics
GET  /api/collective/trends             # Time-based collective trends
```

---

## DATA STRUCTURE

### MongoDB Collections

#### `users`
```javascript
{
  id: string,              // UUID
  email: string,           // Lowercase email
  password_hash: string,   // bcrypt hash
  created_at: string,      // ISO timestamp
  last_login_at: string    // ISO timestamp
}
```

#### `philos_sessions`
```javascript
{
  user_id: string,
  history: [               // Last 20 decisions
    {
      action: string,
      decision: string,    // "Allowed" | "Blocked"
      chaos_order: number,
      ego_collective: number,
      balance_score: number,
      value_tag: string,
      time: string,
      timestamp: string
    }
  ],
  global_stats: {
    contribution: number,
    recovery: number,
    order: number,
    harm: number,
    avoidance: number,
    totalDecisions: number,
    sessions: number
  },
  trend_history: [         // Last 30 days
    {
      date: string,
      timestamp: string,
      totalDecisions: number,
      contribution: number,
      recovery: number,
      order: number,
      harm: number,
      avoidance: number
    }
  ],
  last_updated: string
}
```

#### `philos_saved_sessions`
```javascript
{
  user_id: string,
  session_id: string,
  name: string,
  timestamp: string,
  history: [...],
  summary: {...}
}
```

#### `philos_decisions`
```javascript
{
  id: string,
  user_id: string,
  action: string,
  decision: string,
  chaos_order: number,
  ego_collective: number,
  balance_score: number,
  value_tag: string,
  time: string,
  timestamp: string
}
```

#### `philos_path_selections`
```javascript
{
  id: string,
  user_id: string,
  selected_path_id: number,
  suggested_action: string,
  predicted_value_tag: string,
  predicted_order_drift: number,
  predicted_collective_drift: number,
  predicted_harm_pressure: number,
  predicted_recovery_stability: number,
  timestamp: string
}
```

#### `philos_path_learning`
```javascript
{
  id: string,
  user_id: string,
  predicted_value_tag: string,
  actual_value_tag: string,
  predicted_order_drift: number,
  actual_order_drift: number,
  predicted_collective_drift: number,
  actual_collective_drift: number,
  predicted_harm_pressure: number,
  actual_harm_pressure: number,
  predicted_recovery_stability: number,
  actual_recovery_stability: number,
  match_quality: string,   // "high" | "medium" | "low"
  timestamp: string
}
```

#### `philos_adaptive_scores`
```javascript
{
  user_id: string,
  contribution: number,    // -20 to +20
  recovery: number,
  order: number,
  harm: number,
  avoidance: number,
  last_updated: string
}
```

---

## DEPLOY PREVIEW

**Live URL:** https://orient-global.preview.emergentagent.com

### Environment Variables

#### Frontend (`/app/frontend/.env`)
```
REACT_APP_BACKEND_URL=https://orient-global.preview.emergentagent.com
```

#### Backend (`/app/backend/.env`)
```
MONGO_URL=<MongoDB connection string>
DB_NAME=<Database name>
JWT_SECRET_KEY=<Secret key for JWT>
CORS_ORIGINS=*
```

---

## Current Product State: Stable MVP

### ✅ Completed Features
1. **Decision Engine** - Core evaluation logic with value tagging
2. **Decision Path Engine** - 3 suggested paths with predictions
3. **Path Learning Layer** - Predicted vs actual comparison
4. **Adaptive Path Engine** - Learning-based scoring adjustments
5. **Persistent Memory Layer** - MongoDB storage with localStorage fallback
6. **User Authentication** - Email/password with JWT
7. **Multi-Device Continuity** - Full data sync across devices
8. **Collective Layer** - Cross-user aggregated analytics
9. **Collective Trends** - Time-based trends with period comparison

### 🎯 Key Metrics
- **19 UI section components**
- **15+ API endpoints**
- **8 MongoDB collections**
- **~3500 lines of backend code**
- **~1100 lines in usePhilosState hook**
- **Hebrew RTL throughout**

### 📋 Future Backlog
1. Password Reset functionality
2. Email Verification on registration
3. Export/Import session data
4. Advanced analytics dashboard
5. Mobile-optimized PWA version

---

## Quick Start (Development)

```bash
# Start services
sudo supervisorctl start all

# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs
tail -f /var/log/supervisor/frontend.*.log

# Restart after changes
sudo supervisorctl restart backend frontend
```

---

**Snapshot Created:** March 8, 2026  
**Author:** Emergent Agent (E1)  
**Status:** STABLE MVP - Ready for Production
