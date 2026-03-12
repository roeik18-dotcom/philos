# Philos Orientation - Session Context Summary

**Project:** Philos Orientation – Mental Navigation System  
**Version:** MVP v1 (Fully Functional)  
**Last Updated:** March 8, 2026  
**Language:** UI in Hebrew (עברית) RTL | Communication in English

---

## 1. Architecture

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Tailwind CSS + SVG |
| Backend | FastAPI (Python async) |
| Database | MongoDB (Motor driver) |
| Persistence | localStorage + MongoDB cloud sync |
| Preview URL | https://decision-engine-lab.preview.emergentagent.com |

---

## 2. Implemented Modules (11 Complete)

| Module | Status | Description |
|--------|--------|-------------|
| Decision Engine | ✅ | Action evaluation, value tagging, balance scoring |
| Personal Map | ✅ | Direction indicators, top values, value graph |
| Collective Value Map | ✅ | Session value distribution, patterns |
| Orientation Field | ✅ | Order/collective drift, harm pressure |
| Global Value Field | ✅ | Cross-session aggregated analytics |
| Global Trend | ✅ | Sparkline charts over time |
| Cloud Sync | ✅ | MongoDB backend, auto-sync, offline fallback |
| Session Library | ✅ | Save/load/delete sessions from cloud |
| Value Constellation Map | ✅ | Spatial SVG visualization of value clusters |
| Session Comparison Engine | ✅ | Compare two sessions side-by-side |
| Weekly Cognitive Report | ✅ | 7-day summary with insights |

---

## 3. Project Structure

```
/app/
├── frontend/src/
│   ├── pages/PhilosDashboard.js       # Main dashboard
│   ├── components/philos/sections/    # 14 section components
│   └── services/cloudSync.js          # Cloud sync service
├── backend/
│   └── server.py                      # API endpoints
└── memory/PRD.md                      # Documentation
```

---

## 4. API Endpoints

```
GET  /api/                                    # Health check
POST /api/philos/sync                         # Sync data
GET  /api/philos/sync/{user_id}               # Get user data
POST /api/philos/sessions/save?user_id={id}   # Save session
GET  /api/philos/sessions/{user_id}           # List sessions
DELETE /api/philos/sessions/{user_id}/{id}    # Delete session
```

---

## 5. Next Steps (Not Started)

1. User Authentication (email/password login)
2. Decision Path Engine (action suggestions)
3. Monthly Reports
4. Mobile App

---

## 6. Key Files to Resume

- `/app/frontend/src/pages/PhilosDashboard.js`
- `/app/backend/server.py`
- `/app/memory/PRD.md`

**Project Status: MVP v1 Complete - Ready for Next Phase**

### Session Management
| Component | File | Description |
|-----------|------|-------------|
| **Session Summary** | `SessionSummarySection.js` | Export JSON, share card |
| **Session Library** | `SessionLibrarySection.js` | Save/load/delete sessions |
| **Session Comparison** | `SessionComparisonSection.js` | Compare two sessions side-by-side |

### Infrastructure
| Component | File | Description |
|-----------|------|-------------|
| **Cloud Sync** | `cloudSync.js` | Auto-sync with MongoDB, offline fallback |
| **Daily Orientation** | `DailyOrientationSection.js` | Daily loop guidance |

---

## 3. Project Structure

```
/app/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── PhilosDashboard.js          # Main dashboard (~1200 lines)
│   │   ├── components/
│   │   │   └── philos/
│   │   │       ├── DecisionMap.js          # 2D map SVG component
│   │   │       └── sections/               # 14 section components
│   │   │           ├── index.js
│   │   │           ├── ActionEvaluationSection.js
│   │   │           ├── CollectiveValueMapSection.js
│   │   │           ├── DailyOrientationSection.js
│   │   │           ├── DecisionMapSection.js
│   │   │           ├── GlobalTrendSection.js
│   │   │           ├── GlobalValueFieldSection.js
│   │   │           ├── OrientationFieldSection.js
│   │   │           ├── PersonalMapSection.js
│   │   │           ├── SessionComparisonSection.js
│   │   │           ├── SessionLibrarySection.js
│   │   │           ├── SessionSummarySection.js
│   │   │           ├── ValueConstellationSection.js
│   │   │           └── WeeklySummarySection.js
│   │   ├── services/
│   │   │   └── cloudSync.js                # Cloud sync service
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
│
├── backend/
│   ├── server.py                           # All API endpoints (~400 lines)
│   ├── requirements.txt
│   └── philos_orientation/                 # Decision engine module
│       ├── __init__.py
│       ├── engine.py
│       ├── decision.py
│       └── models.py
│
└── memory/
    └── PRD.md                              # Full documentation
```

---

## 4. API Endpoints

### Health & Status
```
GET  /api/                              → {"message": "Hello World"}
```

### Cloud Sync
```
POST /api/philos/sync                   → Sync local data with cloud
GET  /api/philos/sync/{user_id}         → Get cloud data for user
```

### Session Library
```
POST /api/philos/sessions/save?user_id={id}    → Save session to library
GET  /api/philos/sessions/{user_id}             → List all saved sessions
GET  /api/philos/sessions/{user_id}/{id}        → Get session details
DELETE /api/philos/sessions/{user_id}/{id}      → Delete session
```

---

## 5. Database Collections (MongoDB)

| Collection | Purpose |
|------------|---------|
| `philos_sessions` | User session data (history, globalStats, trendHistory) |
| `philos_saved_sessions` | Session Library entries with full history |
| `status_checks` | Health check records |

---

## 6. Key Data Models

### Decision Record
```javascript
{
  action: string,
  decision: "Allowed" | "Blocked",
  chaos_order: number,      // -100 to 100
  ego_collective: number,   // -100 to 100
  balance_score: number,    // 0 to 100
  value_tag: "contribution" | "recovery" | "order" | "harm" | "avoidance",
  time: string,
  timestamp: string (ISO)
}
```

### Session Snapshot (Trend History)
```javascript
{
  date: string (YYYY-MM-DD),
  timestamp: string (ISO),
  totalDecisions: number,
  contribution: number,
  recovery: number,
  harm: number,
  order: number,
  avoidance: number
}
```

### Global Stats
```javascript
{
  contribution: number,
  recovery: number,
  harm: number,
  order: number,
  avoidance: number,
  totalDecisions: number,
  sessions: number
}
```

---

## 7. localStorage Keys

| Key | Content |
|-----|---------|
| `philos_session_data` | Current session state, history, decisionResult |
| `philos_global_data` | Aggregated global statistics |
| `philos_trend_history` | Array of session snapshots for trends |
| `philos_user_id` | Auto-generated user identifier |
| `philos_last_sync` | Last cloud sync timestamp |

---

## 8. Value System

### Value Tags
| Tag | Hebrew | Color | Description |
|-----|--------|-------|-------------|
| contribution | תרומה | Green | Helping others, social positive |
| recovery | התאוששות | Blue | Self-care, rest, restoration |
| order | סדר | Indigo | Organizing, structuring, focus |
| harm | נזק | Red | Negative actions, anger |
| avoidance | הימנעות | Gray | Escaping, postponing |

### Metrics Formulas
- **Order Drift:** (order + recovery) - (harm + avoidance)
- **Collective Drift:** contribution - harm
- **Harm Pressure:** harm / total × 100
- **Recovery Stability:** recovery / total × 100
- **Balance Score:** 100 - (|chaos_order| + |ego_collective|)

---

## 9. Current Product State

### Completed Features ✅
1. Decision Engine with value tagging
2. Personal Map with value graph
3. Collective Value Map
4. Orientation Field metrics
5. Global Value Field (cross-session)
6. Global Trend sparklines
7. Cloud Sync (MongoDB)
8. Session Library (save/load/delete)
9. Value Constellation Map (SVG)
10. Session Comparison Engine
11. Weekly Cognitive Report

### Pending / Next Steps
1. **User Authentication** (was in progress)
   - Backend endpoints: /api/auth/register, /api/auth/login
   - MongoDB users collection
   - JWT tokens
   - Frontend login screen

2. **Future Backlog:**
   - Monthly summary report
   - Export weekly report as PDF
   - Social features (community sharing)
   - Mobile app (React Native)
   - AI-powered decision suggestions

---

## 10. Development Notes

### Commands
```bash
# Restart services
sudo supervisorctl restart frontend
sudo supervisorctl restart backend

# View logs
tail -n 50 /var/log/supervisor/frontend.err.log
tail -n 50 /var/log/supervisor/backend.err.log

# Test API
API_URL=https://decision-engine-lab.preview.emergentagent.com
curl -s "$API_URL/api/"
```

### Code Style
- Hebrew text for all UI labels
- RTL layout throughout
- Tailwind CSS for styling
- SVG for visualizations (no heavy chart libraries)
- Functional React components with hooks

### Testing
- Screenshots for visual verification
- curl for API testing
- localStorage seeding for data testing

---

## 11. Preview URL

**Live App:** https://decision-engine-lab.preview.emergentagent.com

---

## 12. Files to Review When Resuming

1. `/app/frontend/src/pages/PhilosDashboard.js` - Main dashboard
2. `/app/frontend/src/services/cloudSync.js` - Sync service
3. `/app/backend/server.py` - All API endpoints
4. `/app/memory/PRD.md` - Full product documentation
5. `/app/README_PROJECT_STATE.md` - Quick reference

---

**Ready for next development session.**
