# Philos Orientation - PRD

## Original Problem Statement
Build "Philos Orientation" — a decision engine and dashboard for real-time decision analysis and mental navigation. Hebrew (RTL) UI.

## Core Loop
**Base → Choice → Action → Field → Reflection**

## Architecture
Frontend: React + Tailwind + Shadcn/UI | Backend: FastAPI + MongoDB | Auth: JWT

## Completed Features

### Phases 1–28 (prior)
Core dashboard, engagement, community, missions, UI polish, referral, validation, demo agents, theory, stabilization, globe, pulse, heartbeat, product rebuild, feed + value + subscription, social, circles, testing prep, profiles, share, engagement loop, orientation map, clarity & meaning, daily base, base loop, invite codes, invite rewards.

### Phase 29 — Human Action Record Redesign (2026-03-12)
Dark documentary profile page: hero with identity markers, stats strip (impact/actions/streak/field%), opposition axes, influence chain with credits, upgraded share card.

### Phase 30 — Highlighted Records Discovery (2026-03-12)
1. **Backend**: `/api/orientation/highlighted-records` — returns top 8 active users (last 7 days) sorted by impact score with alias, dominant_direction, impact_score, invite_count
2. **Frontend**: `HighlightedRecords.js` — horizontal scrollable dark cards at top of Feed tab
   - "אנשים בשדה" (People in the field) label
   - Cards show: direction-colored initial, alias, direction badge (Hebrew), impact score, invite icon+count
   - Clicking opens `/profile/{user_id}` Human Action Record
3. **No social mechanics** — observation and navigation only, no likes/comments/follow

## Key API Endpoints
| Endpoint | Method | Returns |
|---|---|---|
| `/api/orientation/highlighted-records` | GET | Top 8 active users with stats |
| `/api/profile/{user_id}/record` | GET | Full profile + field_contribution + influence_chain |
| `/api/orientation/invite-stats/{user_id}` | GET | Codes + credits + active invitees |
| `/api/orientation/daily-answer/{user_id}` | POST | Action + invite reward |
| `/api/orientation/daily-base/{user_id}` | GET/POST | Base selection |
| `/api/orientation/daily-question/{user_id}` | GET | Base-influenced question |
| `/api/orientation/day-summary/{user_id}` | GET | Summary + dept + reflection |
| `/api/orientation/field-dashboard` | GET | Field narrative |

## Backlog
### P0
- AI Interpretation layer (deferred)
- Real-user observation
### P1
- Refactor server.py into modules
### P2
- Department weekly insights, time-of-day narratives, private circles
