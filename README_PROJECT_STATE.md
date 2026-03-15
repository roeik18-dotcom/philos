# Philos Orientation

**Current Version:** MVP v1  
**Last Updated:** March 7, 2026  
**Status:** Complete - Ready for next phase

---

## Core Features

| Feature | Status | Description |
|---------|--------|-------------|
| Decision Engine | ✅ | Action evaluation, value tagging (contribution/recovery/harm/order/avoidance), balance scoring |
| Personal Map | ✅ | Direction indicators, top values, decision timeline, value graph |
| Collective Map | ✅ | Session value distribution, collective patterns summary |
| Orientation Field | ✅ | Order drift, collective drift, harm pressure, recovery stability |
| Global Value Field | ✅ | Cross-session analytics, dominant value cluster, global distribution |
| Global Trend | ✅ | Sparkline charts over time, trend insights, auto-save snapshots |
| Cloud Sync | ✅ | MongoDB backend, auto-sync, offline fallback, sync status indicator |
| Session Library | ✅ | Save/load/delete sessions, browsable cards with metrics |

---

## Tech Stack

- **Frontend:** React 18, Tailwind CSS, SVG visualizations
- **Backend:** FastAPI, MongoDB (Motor async driver)
- **Persistence:** localStorage (offline) + MongoDB (cloud)
- **Export:** html-to-image (PNG), JSON download

---

## Project Structure

```
/app/
├── frontend/
│   └── src/
│       ├── pages/PhilosDashboard.js          # Main dashboard
│       ├── components/philos/sections/        # 10 UI components
│       └── services/cloudSync.js              # Cloud sync service
├── backend/
│   ├── server.py                              # API endpoints
│   └── philos_orientation/                    # Decision engine
└── memory/
    └── PRD.md                                 # Full documentation
```

---

## API Endpoints

```
GET  /api/                                    # Health check
POST /api/philos/sync                         # Sync data with cloud
GET  /api/philos/sync/{user_id}               # Get user cloud data
POST /api/philos/sessions/save?user_id={id}   # Save session
GET  /api/philos/sessions/{user_id}           # List sessions
GET  /api/philos/sessions/{user_id}/{id}      # Get session
DELETE /api/philos/sessions/{user_id}/{id}    # Delete session
```

---

## Preview URL

https://philos-mvp.preview.emergentagent.com

---

## Next Development Priorities

1. **User Authentication** - Email/password or Google OAuth
2. **Multi-device Support** - Login to access data anywhere
3. **Session Comparison** - Compare two sessions side by side
4. **Social Features** - Share with community

---

## Language

- **UI:** Hebrew (עברית) with RTL layout
- **User Communication:** English
