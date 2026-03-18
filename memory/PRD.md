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

### Action Flow & Visibility System (Complete - March 2026)
- 3-step post wizard: Create → Visibility → Publish with step indicators
- Step 1 (Create): title, description, category, community, location with geolocation detect
- Step 2 (Visibility): Public (reactions→trust→profile flow) or Private (personal record)
- Step 3 (Review): preview with visibility badge, trust flow steps 4-5-6 for public
- Post success: "Action Published" with outcome indicators (Reactions→Trust Score→Profile)
- Feed: visibility tabs (All/Public/My Private), visibility badges on cards
- Backend: visibility field on actions, feed filtered by visibility + viewer_id
- Private actions only visible to owner, no reactions, no trust impact
- Trust outcome indicator on feed cards (score → profile arrow)
- Files: PostAction.js (rewrite), ActionFeed.js (tabs/badges), actions.py (visibility), app.css

### Position Bar — Self ↔ Network Spectrum (Complete - March 2026)
- Persistent position bar across feed, profile, and post pages
- GET /api/position/{user_id}: calculates 0.0 (Self) to 1.0 (Network) score
- 4 factors: public actions (max 0.35), unique reactors (max 0.25), trust (max 0.25), active referrals (max 0.15)
- Private actions do NOT affect position — only public engagement counts
- Labels: Self → Emerging → Contributing → Connected → Network
- Visual: gradient fill bar, glowing cyan marker, factor tag pills
- PositionBar.js shared component with AbortController, conditional rendering for logged-in users
- Files: trust_integrity.py (position endpoint), PositionBar.js, ActionFeed.js, ProductProfile.js, PostAction.js, app.css

### Daily Orientation Layer (Complete - March 2026)
- Rule-based guidance card: one recommendation per user based on position + trust + activity
- GET /api/orientation/{user_id}: returns message, action_type, cta, context
- Decision rules (first match wins):
  1. No actions → "Post your first action"
  2. Only private → "Make one action visible"
  3. Inactive 7+ days → "Post one action to maintain position"
  4. Self → "Publish public action to move toward Emerging"
  5. Emerging + low reactors → "Engage with others' actions"
  6. Emerging → "Keep posting to move toward Contributing"
  7. Contributing + no referrals → "Share to invite others"
  8. Contributing → "Engage more to move toward Connected"
  9. Connected → "Keep contributing"
  10. Network → "Verify others' actions"
- OrientationCard.js: compass icon, message, contextual CTA button
- Displayed on feed (after position bar) and profile (after position bar)
- CTA navigates to post or feed based on action_type
- Files: trust_integrity.py (orientation endpoint), OrientationCard.js, ActionFeed.js, ProductProfile.js, ProductApp.js, app.css

### Position Status Layer — Movement-Based Trajectory (Complete - March 2026)
- Status determined by MOVEMENT, not time alone: position_delta + trust_delta + recent_activity
- 4 statuses with deterministic rules (first match wins):
  1. At Risk: active risk signals OR 14+ days inactive with 0 activity
  2. Rising: (position increased OR trust increased) AND recent activity (3d)
  3. Decaying: inactive 7+ days OR negative position/trust change
  4. Stable: active, no significant change (default)
- Comparison via position_snapshots collection (one per user per day)
- First snapshot approximated from current values
- Backend: utils/status_calculator.py (pure function), integrated into GET /api/position/{user_id} and GET /api/orientation/{user_id}
- Frontend: PositionBar.js shows status badge with icon + label; OrientationCard.js shows status tag
- Orientation messages are status-aware (At Risk mentions risk signals, Decaying urges action)
- Status metadata: icon (up/right/down/warning), label, color, reason
- Files: utils/status_calculator.py, trust_integrity.py, PositionBar.js, OrientationCard.js, app.css

### Status Consequence Layer — Product-Level Visibility Effects (Complete - March 2026)
- Status now affects feed ranking and action visibility, not just display
- Consequence multipliers (deterministic):
  - Rising: 1.15x visibility boost
  - Stable: 1.00x neutral
  - Decaying: 0.85x reduction
  - At Risk: 0.70x stronger reduction + warning state
- Enforcement override: active risk signals always cap multiplier at 0.70x (ENFORCEMENT_CAP)
- Feed ranking formula: rank_score = (recency*50 + trust*2 + reactions*3) * author_multiplier
  - recency decays linearly from 1.0 to 0.0 over 168 hours (7 days)
  - Feed sorted by rank_score descending (no longer pure chronological)
- Batch author multiplier computation via _get_author_multipliers() using position_snapshots + risk_signals
- rank_score and visibility_weight added to every action in feed response
- consequence_multiplier field added to position and orientation endpoint responses
- Orientation messages updated to mention consequences:
  - At Risk: "your actions have reduced visibility"
  - Decaying: "your actions are losing visibility"
  - Rising: "your actions are getting boosted"
- Files: utils/status_calculator.py (multipliers), actions.py (ranking), trust_integrity.py (responses+messaging)

### Consequence Transparency Panel (Complete - March 2026)
- Minimal panel on profile page: status, multiplier, meaning, next step
- Backend: get_consequence_panel() in status_calculator.py returns {meaning, next_step}
- Panel data included in GET /api/position/{user_id} as consequence_panel field
- Next-step rules by status:
  - At Risk + risk signals: "Post authentic public actions to begin resolving risk signals"
  - At Risk + inactivity: "Post 1 public action to start recovering toward Decaying"
  - Decaying + inactive: "Post 1 public action to recover toward Stable"
  - Decaying + negative change: "Continue posting to stabilize your position"
  - Stable: "Post 1 more public action to move toward Rising"
  - Rising: "Keep it up — maintain activity to keep your boost"
- Frontend: ConsequencePanel.js component, placed on ProductProfile.js
- Visual: header "Action Visibility", status pill, multiplier (red/green/neutral), meaning, cyan next-step
- Files: status_calculator.py, trust_integrity.py, ConsequencePanel.js, ProductProfile.js, app.css

### Recovery Progress Indicator (Complete - March 2026)
- Minimal progress indicator for Decaying/At Risk users only (null for Rising/Stable)
- Shows: current status, target status, one requirement, progress bar
- Recovery paths (deterministic, one per status):
  - At Risk (risk signals) → Decaying: need 3 recent public actions
  - At Risk (inactivity) → Stable: need 1 recent public action
  - Decaying (inactivity) → Stable: need 1 recent public action
  - Decaying (negative change) → Stable: need 2 recent public actions
- When action target met but risk signals remain: "Actions met — risk signals still active"
- Backend: get_recovery_progress() in status_calculator.py, added to position endpoint as recovery_progress
- Frontend: integrated into ConsequencePanel.js with progress bar (cyan #00d4ff)
- Files: status_calculator.py, trust_integrity.py, ConsequencePanel.js, app.css

### Status Change Notification (Complete - March 2026)
- Subtle toast notification on login/page load when user's status changed since last seen
- Persistence: last_seen_status stored in localStorage per user (key: philos_last_status_{userId})
- Notification rules:
  - Only fires when previous status exists AND differs from current
  - Does not repeat once acknowledged (localStorage updated immediately)
  - Downward changes: toast.error() with 8s duration (red icon)
  - Upward changes: toast.success() with 6s duration (green icon)
  - Neutral: toast() with 6s duration
- Messages include previous + new status + one explanation:
  - Down: "Your status dropped to At Risk — your actions have reduced visibility. Take action to recover."
  - Up: "You recovered from Decaying to Stable — your visibility is back to normal."
- Uses sonner toast library, rendered via Toaster in ProductApp.js (dark theme, top-center)
- StatusChangeNotifier is a renderless component (returns null)
- Files: StatusChangeNotifier.js, ProductApp.js

### Action Flow — Behavioral Engine (Complete - March 2026)
- Replaced bottom tab navigation with a 6-step dynamic action flow: Need → Choice → Action → Reaction → Result → Reward
- Each step is interactive with real user data:
  1. Need: position/status/trust + orientation suggestion (from /api/position + /api/orientation)
  2. Choice: public vs private action selection
  3. Action: simplified post form (title, description, category) → POST /api/actions/post
  4. Reaction: live engagement data (reactions, trust signal, visibility weight)
  5. Result: position delta, trust delta, status change (baseline vs fresh fetch)
  6. Reward: consequence multiplier + meaning + next step
- Animated transitions between steps (slide forward/backward)
- Step indicator bar at bottom (replaces bottom nav when flow is active)
- Back navigation on pre-submit steps only (steps 0-2)
- Flow resets on completion (Done button)
- Bottom tab bar hidden during flow (flow has its own step bar)
- 'Post' nav replaced with 'Flow' (Zap icon) in NAV_ITEMS
- Files: ActionFlow.js (new), ProductApp.js (updated), app.css (flow styles)

### Action Flow — Real-User Testing Optimization (Complete - March 2026)
- Simplified Step 1 (Need): single entry message + one insight (was 3-card grid)
  - First-time users: "Post one action to see how the system works."
  - Returning users: "One action moves your position."
  - One insight card with status-colored dot + orientation message
- Simplified Step 3 (Action): removed category pills, description optional, single "Publish" CTA
  - Only title required to submit
  - Category defaults to 'community' internally
- Goal: maximize first-time flow completion rate
- Files: ActionFlow.js, app.css

### Backend Wake System — Invisible Cold Start Handling (Complete - March 2026)
- Silent backend wake: /api/health endpoint pinged every 2.5s on app load
- Minimal branded loading state: just "Philos" text with subtle pulse — no spinners, no technical messages
- Auth check gated by isReady signal (runs only after backend responds)
- Action queue: enqueue() stores lambdas that execute when backend is ready
- ActionFlow handlePost uses enqueue fallback for pre-ready submissions
- Retry logic: AbortController with 4s timeout, silent retry every 2.5s
- User never sees backend state — system feels instantly responsive
- Files: server.py (health endpoint), useBackendReady.js (new hook), App.js (provider + wake screen), ActionFlow.js (enqueue), App.css (wake styles)

### Production 404 Fix (Complete - March 2026)
- Added SPA fallback files: `_redirects` (Netlify/CDN), `vercel.json`, `static.json`
- All route `/*` to `/index.html` with 200 status
- Fixed JWT_SECRET_KEY: removed hardcoded fallback, now uses env var only
- Added `homepage: "/"` to package.json for correct asset paths in production build
- Verified: production build includes index.html + _redirects at root
- All routes (/, /app, /app/feed, /app/flow, /trust-test) return 200
- Files: _redirects, vercel.json, static.json, package.json, auth_utils.py, backend/.env

## Prioritized Backlog

### P2: Risk Signal Framework — Remaining Work
- Build admin UI to view/manage risk signals (currently API-only)

### P2: Expand Trust-Aware AI
### P3: ProfilePage Refactoring
### P3: Legacy Hebrew DB Data Migration

## Test Credentials
- Email: `newuser@test.com` | Password: `password123`
- Email: `trust_fragile@test.com` | Password: `password123`
