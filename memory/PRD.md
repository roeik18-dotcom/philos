# Philos Orientation - Product Requirements Document

## Original Problem Statement
Build a comprehensive "Value + Risk + Trust" system for the "Philos Orientation" application. The project has evolved through several phases, culminating in a full Hebrew-to-English translation to prepare for public launch to an English-speaking audience.

## Core System
- **V+R+T Engine**: Value, Risk, and Trust scoring system
- **Automated Daily Score Decay**: APScheduler-based background job
- **User Invite System**: Code-based invites with tracking and rewards
- **Lightweight Analytics**: Event tracking and funnel analysis
- **Trust Test Page**: Public `/trust-test` page for measuring trust
- **AI Interpretation Layer**: Claude Sonnet 4.5 powered profile insights

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Pydantic + MongoDB
- **AI**: Claude Sonnet 4.5 via `emergentintegrations`
- **Visualization**: react-globe.gl, three.js
- **Payments**: Stripe
- **Scheduling**: APScheduler

## Launch Status: READY
- All user-facing text: English
- Layout: LTR
- Analytics: Tracking and funnel working
- Auth: Register, login, logout — all English
- Trust test flow: End-to-end verified
- Onboarding: English
- Dashboard: English
- Invite system: English
- Backend: 18/18 tests passed
- Frontend: 100% English, LTR verified
- Hebrew in production code: Zero

## Key Funnel Steps (tracked)
landing_view → start_clicked → base_selected → question_answered → trust_shown → invite_copied

## Key API Endpoints
- `POST /api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `GET /api/auth/me`
- `GET /api/orientation/field-today`, `/api/orientation/field`, `/api/orientation/history`
- `GET /api/decision-path/{user_id}`, `/api/orientation/identity/{user_id}`
- `GET /api/orientation/daily-question/{user_id}`, `POST /api/orientation/daily-answer/{user_id}`
- `GET /api/orientation/weekly-insight/{user_id}`, `/api/orientation/compare/{user_id}`
- `POST /api/onboarding/first-action`
- `POST /api/analytics/track` (payload: `{event, user_id, metadata}`)
- `GET /api/analytics/funnel`
- `GET /api/system/status`
- `GET /api/invites/me`, `POST /api/invites/generate`, `POST /api/invites/redeem`
- `POST /api/feedback`

## Prioritized Backlog
### P1: Expand Trust-Aware AI
- Extend trust context to action and field interpretation layers

### P2: Define and Map Risk Signals
- Define risk signals based on user behavior patterns

### P2: ProfilePage Refactoring
- Break down ProfilePage.js (809 lines) into smaller components

### P3: Legacy Data Migration (Optional)
- Migrate existing Hebrew daily questions in DB for legacy users

## Test Credentials
- Email: `newuser@test.com` | Password: `password123`
- Email: `trust_fragile@test.com` | Password: `password123`
