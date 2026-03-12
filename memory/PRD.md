# Philos Orientation - Product Requirements Document

## Original Problem Statement
A Hebrew (RTL) philosophical orientation application where users engage in daily actions, observe a collective "human field" via a 3D globe, and build personal value profiles. The app uses an invite-based growth model and features an AI Interpretation Layer for symbolic, philosophical observations.

## Core Architecture
- **Frontend:** React, react-router-dom, react-globe.gl, three.js, Shadcn UI. Hebrew RTL.
- **Backend:** FastAPI (monolithic server.py), Pydantic, Pymongo (Motor async), passlib, python-jose.
- **Database:** MongoDB
- **AI:** Claude Sonnet 4.5 via emergentintegrations library with Emergent LLM Key.
- **Other:** html-to-image (share cards), Stripe (subscriptions).

## Key Files
- `/app/backend/server.py` — Monolithic backend with all routes, models, services
- `/app/backend/philos_ai.py` — AI Interpretation Layer (Claude Sonnet 4.5)
- `/app/frontend/src/pages/PhilosDashboard.js` — Main dashboard
- `/app/frontend/src/pages/ProfilePage.js` — Human Action Record (public profile)
- `/app/frontend/src/components/philos/sections/GlobalFieldDashboard.js` — Field dashboard with AI interpretation
- `/app/frontend/src/components/philos/sections/DailyOrientationQuestion.js` — Daily question with AI action interpretation

## Implemented Features (Complete)
1. World State & Globe UI with symbolic narrative
2. Opposition Engine (personal tension mirror)
3. Daily Base Allocation System (Heart, Head, Body)
4. Base-Influenced Daily Questions
5. Invite System (PH-XXXX codes, limits, tracking)
6. Invite Reward System (value credits for inviter)
7. Human Action Record (public profile page)
8. Profile Discovery (Highlighted Records in Feed)
9. Presence Indicator (24h activity pulse)
10. **AI Interpretation Layer (Claude Sonnet 4.5)** — Verified 2026-03-12
    - Action Interpretation: after daily answer (POST /api/orientation/daily-answer)
    - Field Interpretation: global dashboard (GET /api/orientation/field-dashboard)
    - Profile Interpretation: human action record (GET /api/profile/{user_id}/record)

## Test Reports
- `/app/test_reports/iteration_58.json` — AI Interpretation Layer: 100% pass (16/16 backend, 3/3 frontend)

## Backlog / Future
- P2: Refactor monolithic server.py into modular routes/models/services
- User direction needed for next feature phase

## Test Credentials
- Email: newuser@test.com
- Password: password123
- User ID: 05d47b99-88f1-44b3-a879-6c995634eaa0
