# Philos Orientation - Product Requirements Document

## Original Problem Statement
Build a comprehensive "Value + Risk + Trust" system for the "Philos Orientation" application. The project has evolved through implementation of the V+R+T engine, full Hebrew-to-English translation, and now an investor-facing visual platform landing page.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Pydantic + MongoDB
- **AI**: Claude Sonnet 4.5 via `emergentintegrations`
- **Visualization**: react-globe.gl, three.js, CSS animations
- **Payments**: Stripe
- **Scheduling**: APScheduler

## Routing
- `/` — Platform landing page (investor-facing, primary entry)
- `/trust-test` — Public trust test flow
- `/dashboard` — Authenticated user dashboard
- `/admin` — Admin panel
- `/profile/{id}` — User profile
- `/invite/{code}` — Invite page

## What's Been Implemented

### Core System (Complete)
- Full V+R+T reputation engine
- User auth, orientation map, daily questions
- Decision path, identity, collective field
- Social features, globe, invite system

### Full English Translation (Complete)
- All frontend and backend translated from Hebrew to English
- LTR layout, English fonts

### Entrance Layer Landing Page (Complete - March 2026)
- Full-screen hero: globe + compass geometry hybrid animated background
- Headline: "Actions build trust." / "Trust shapes opportunity."
- Primary CTA: "Enter the App" → /app/feed (pill button, cyan accent)
- Layer 1: react-globe.gl at 45% opacity with auto-rotation
- Layer 2: CSS compass geometry (3 rotating rings, crosshairs, tick marks)
- Layer 3: Gradient overlays (top/bottom fade to background)
- Three micro-message blocks: Action→Trust, Trust→Visibility, Visibility→Opportunity
- Scroll-reveal animation via IntersectionObserver
- Parallax scroll on background (0.15x speed)
- Bottom CTA + minimal "PHILOS" footer
- Responsive: 768px/480px breakpoints
- Files: PlatformLandingPage.js (complete rewrite), platform.css (complete rewrite)

### SEO & Indexing (Complete - March 2026)
- sitemap.xml for all public pages (/, /trust-test)
- robots.txt allowing all crawlers
- Google Analytics GA4 (G-5MNK51HSQ1) active
- Google Search Console verification tag active
- Updated meta title, description, keywords
- Open Graph tags (og:title, og:description, og:type, og:url, og:site_name, og:locale)
- Twitter Card meta tags
- Canonical URL tag
- Files: sitemap.xml, robots.txt, index.html

### Product MVP (Complete - March 2026)
- 5 pages built under `/app` routes with shared layout and navigation
- `/app/feed` — Action Feed with category filters, action cards (title, description, category, location, contributor, community, timestamp)
- `/app/post` — Post Action form (auth required) with Title, Description, Category, Community, Location + geolocation detect
- `/app/map` — Impact Map using Leaflet + dark CartoCDN tiles, colored markers by category, popups with action details
- `/app/profile` — User profile with avatar, stats (Actions, Impact Score, Verified), contribution categories, communities
- `/app/dashboard` — Daily dashboard with summary stats, network activity, suggested actions
- Auth gating: Post/Profile/Dashboard require sign-in
- Full E2E flow verified: Post → Feed → Map
- Mobile responsive with bottom tab bar
- OG image (1200x630) for social sharing added
- Files: ProductApp.js, ActionFeed.js, PostAction.js, ImpactMap.js, ProductProfile.js, DailyDashboard.js, app.css

### Reactions & Trust Score System (Complete - March 2026)
- 3 reaction types on every action card: Support (+1), Useful (+2), Verified (+5)
- Toggle on/off with optimistic UI updates
- Trust Score per action (displayed as badge when > 0)
- Aggregate Trust Score per user in profile
- Feed endpoint supports viewer_id for user_reacted flags
- Profile shows 4 stats: Trust Score, Actions, Impact Score, Verified
- Files modified: ActionFeed.js, ProductProfile.js, app.css, actions.py

### Share Action Feature (Complete - March 2026)
- Share button on every feed card opens modal with preview (user, title, community, trust score)
- 4 share options: Copy Link, WhatsApp, LinkedIn, Twitter/X
- Shareable action page at /app/action/{id} with full preview card
- Backend GET /api/actions/{action_id} endpoint for single action lookup
- Files: ActionFeed.js (ShareModal), ActionSharePage.js, app.css, actions.py

### Dynamic OG Tags (Complete - March 2026)
- Backend-rendered HTML at /api/share/action/{id} with dynamic OG + Twitter meta tags
- Server-side OG image generation (1200x630) with Pillow: avatar, title, community, trust score, Philos branding
- Social share URLs updated to use /api/share/action/{id} for WhatsApp/LinkedIn/Twitter
- Meta refresh redirect to SPA for real users
- Files: og_share.py

### Opportunity System (Complete - March 2026)
- 8 seeded opportunities (jobs, grants, collaborations, support) with trust score requirements
- /app/opportunities page with type filters and Eligible/Locked status
- Progress bar shows unlock count
- Opportunities preview in user profile (top 3)
- Files: opportunities.py, OpportunitiesPage.js, ProductProfile.js

### Community Funds (Complete - March 2026)
- 5 seeded communities with fund data (raised, distributed, balance)
- /app/community-funds leaderboard with expandable transaction history
- Summary stats: total raised, distributed, balance
- Files: community.py, CommunityFundsPage.js

### Leaderboard (Complete - March 2026)
- /app/leaderboard with users ranked by trust score (MongoDB aggregation)
- Top 3 podium display
- Per-user stats: trust score, total actions, categories
- Files: leaderboard.py, LeaderboardPage.js

### Weekly Impact Report (Complete - March 2026)
- /app/report (auth required) with weekly summary
- Stats: week actions, trust earned, total trust, rank, categories, communities
- Network-wide stats: active users, total actions, trust generated
- All-time summary with rank
- Files: leaderboard.py, WeeklyReportPage.js

### Trust Integrity Layer (Complete - March 2026)
- Verification signals: self_reported (1x), community_verified (2x), org_verified (3x) with trust multiplier
- Anti-spam: rate limit (5/hour), duplicate detection (24h), self-reaction prevention (403)
- Reputation decay: 30-day inactivity → 5% trust reduction (scheduled 04:00 UTC daily)
- Community verification endpoint with upgrade-only logic
- Suspicious activity flags: reaction farming + velocity spike detection
- Admin endpoints: /api/trust/integrity-stats, /api/trust/flags
- Frontend verification badges (BadgeCheck green, Building2 amber)
- Files: trust_integrity.py, actions.py updated, scheduler.py updated, ActionFeed.js

### Risk Signal Framework (Complete - March 2026)
- 8 core risk signals across 4 categories (trust_manipulation, content_integrity, account_behavior, network_anomaly)
- Detection logic for 6 new signals (reciprocal_boosting, low_effort_content, category_flooding, ghost_reactor, burst_and_vanish, community_monopoly)
- 2 existing inline signals (reaction_farming, velocity_spike) documented in framework
- All 8 signals inferable from existing data — no new instrumentation needed
- Scanner endpoint: POST /api/risk-signals/scan
- Management endpoints: GET definitions, list, summary, per-user; PATCH status
- Data model: risk_signals collection with signal_type, category, severity, subject_user_id, related_user_ids, related_action_ids, evidence, status, system_response, timestamps
- **Enforcement layer**: integrated into recalc_trust_signal() with safe fallback
  - velocity_spike: freezes trust score (no recalculation)
  - reaction_farming: fully suppresses flagged reactor's contributions
  - reciprocal_boosting: 0.5x discount on mutual reactions
  - ghost_reactor: 0.5x weight on ghost reactor reactions
  - community_monopoly: 0.5x cap on monopolized community trust
  - burst_and_vanish: 10% accelerated decay (vs standard 5%)
- **Scheduler**: daily scan at 05:00 UTC via APScheduler (idempotent, upsert-based)
- Files: risk_signals.py, risk_signal_models.py, trust_integrity.py (enforcement), scheduler.py (scan job)

### Trust Engine API (Complete - March 2026)
- GET /api/trust/{user_id}: returns enforcement-adjusted trust_score, decay_rate, decay_status, active_risk_signals, trust_flags, enforcement_active, last_updated
- Profile page: Trust Engine card with large score, enforcement badge, decay info, active risk signal list with severity labels
- Feed: reaction buttons show trust impact weights (+1/+2/+5), own-action reactions disabled with tooltip
- All values enforcement-adjusted (community_monopoly 0.5x, velocity_spike freeze, etc.)
- Files: trust_integrity.py (endpoint), ProductProfile.js (Trust Engine card), ActionFeed.js (weight labels), app.css (styles)

### Growth Loop — Shareable Actions + Referral Tracking (Complete - March 2026)
- Share URLs include `?ref={userId}` referral parameter when user is logged in
- OG share route passes ref param through to SPA redirect
- Public action page at `/app/action/{id}` shows trust score, reactions, referral CTA
- ActionSharePage stores ref info in localStorage for registration flow
- Registration accepts `referral_user_id` + `referral_action_id`, creates referral record
- `referrals` collection: inviter_id, invited_user_id, action_id, source, created_at
- GET /api/referrals/{user_id} returns referrals made by that user
- Share modal: Copy Link, WhatsApp, LinkedIn, Twitter — all with ref param
- Files: og_share.py, auth.py (referral endpoints), schemas.py, ActionSharePage.js, ActionFeed.js (ShareModal), AuthScreen.js

### Referral Visibility & Reputation Impact (Complete - March 2026)
- Profile shows "People You Brought to Philos" with count badges (total, active, pending)
- Referral list: display name, avatar, status badge (active/pending), trust score, action count
- Referral status: pending (joined, 0 posts) → active (posted 1+ actions)
- Trust bonus: +2 per active referral, added to trust_score in /api/trust/{user_id}
- GET /api/referrals/{user_id}: enriched with status, display_name, trust_score, action_count, active_count, pending_count, referral_trust_bonus
- Trust engine card shows referral bonus in meta section
- Files: auth.py (enriched referrals), trust_integrity.py (referral bonus), ProductProfile.js (referral section), app.css

## Prioritized Backlog

### P2: Risk Signal Framework — Remaining Work
- Build admin UI to view/manage risk signals (currently API-only)

### P2: Expand Trust-Aware AI
### P3: ProfilePage Refactoring
### P3: Legacy Hebrew DB Data Migration

## Test Credentials
- Email: `newuser@test.com` | Password: `password123`
