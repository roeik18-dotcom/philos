# Philos Orientation - Mental Navigation System

## Product Overview
A client-side decision engine and dashboard that provides real-time decision analysis and mental navigation. Features Hebrew RTL interface with tabbed navigation (Home, Insights, System, Theory, History).

## Original Problem Statement
Build a sophisticated single-page tool for decision analysis, behavioral tracking, and self-orientation with cloud sync (MongoDB) and user authentication.

## Core Theoretical Model
The system is based on **four directions** and **two axes**:

### Four Directions
1. **Recovery (התאוששות)** - Returning to balance after stress or harm
2. **Order (סדר)** - Creating structure, organization, and clarity  
3. **Contribution (תרומה)** - Acting for the benefit of others
4. **Exploration (חקירה)** - Openness, flexibility, and forward movement

### Two Tension Axes
1. **Chaos ↔ Order** - Between spontaneity and structure
2. **Ego ↔ Collective** - Between self-focus and focus on others

### Balancing Paths (Theory-Driven)
- **harm → recovery** - Harmful actions require recovery balance
- **avoidance → order** - Avoidance is balanced by creating structure
- **isolation → contribution** - Self-focus is balanced by contributing to others
- **rigidity → exploration** - Stagnation is balanced by openness

---

## Implementation Status (March 2026)

### ORIENTATION FIELD (Collective Navigation Layer) ✅
**Status:** Complete (March 10, 2026)

**What was built:**
1. **Collective Center Calculation** - Aggregates all user data to calculate weighted center position
2. **Collective Center on Compass** - Violet dot marker showing collective position
3. **Drift Visualization** - Dashed line connecting user position to collective center
4. **Alignment Score** - 0-100% score with color coding (green >70%, amber >40%, red <40%)
5. **Insights Generation** - Hebrew insights about user-collective alignment
6. **Collective Momentum Indicator** - Shows field movement trend with directional arrow

**Momentum Calculation:**
- Compares last 7 days vs previous 7 days activity
- Classifies field state as: `stabilizing`, `drifting`, `shifting`, or `stable`
- When shifting, identifies target direction (recovery/order/contribution/exploration)
- Generates Hebrew insights: "השדה הקולקטיבי נע בהדרגה לכיוון סדר"

**Backend Endpoints:**
- `GET /api/orientation/field` - Returns collective distribution, center, momentum, arrow coordinates
- `GET /api/orientation/user/{user_id}` - Returns user position, alignment, drift pattern

**API Response includes:**
- `field_momentum`: stabilizing | drifting | shifting | stable
- `momentum_direction`: Which direction the field is shifting toward
- `momentum_strength`: 0-100 strength of movement
- `momentum_arrow`: {from_x, from_y, to_x, to_y} for visualization
- `momentum_insight`: Hebrew text explaining the trend

**Frontend Visualization:**
- Momentum arrow on compass (violet, animated) when field is not stable
- Momentum indicator box with icon, insight text, and strength bar
- Icon changes based on momentum state (checkmark for stabilizing, warning for drifting, arrow for shifting)

**Test Results:** 100% pass (17/17 tests - 11 backend, 6 frontend)

---

### Historical Momentum Tracking (4 Weeks Sparkline) ✅
**Status:** Complete (March 10, 2026)

**What was built:**
1. **Weekly Snapshots** - Backend calculates field position for each of the last 4 weeks
2. **Sparkline Visualization** - SVG line chart showing positive_ratio trend over time
3. **Trend Detection** - Analyzes movement patterns across weeks
4. **Hebrew Insights** - e.g., "השדה הקולקטיבי נע בהדרגה לכיוון סדר בשבועות האחרונים."

**Backend Endpoint:**
- `GET /api/orientation/history` - Returns 4 weeks of historical data

**API Response includes:**
- `weekly_snapshots`: Array of 4 weeks with center_x, center_y, dominant_direction, positive_ratio, total_actions
- `sparkline_data`: Array of positive_ratio values for visualization
- `trend_type`: stabilizing | drifting | shifting_* | stable
- `trend_direction`: Target direction if shifting
- `trend_insight`: Hebrew explanation of the trend

**Frontend Visualization:**
- SVG sparkline with data points and gradient fill
- Week labels in Hebrew (שבוע 1, שבוע 2, שבוע 3, השבוע)
- Weekly dots showing dominant direction color
- Action count per week
- Trend badge (מתייצב/נסחף/משתנה)

**Test Results:** 100% pass (19/19 backend tests, all frontend elements verified)

---

### User Comparison Features (Percentile Ranking) ✅
**Status:** Complete (March 10, 2026)

**What was built:**
1. **Percentile Calculation** - Compares user's activity in each direction against all other users
2. **Rank Labels** - "עליון 10%", "עליון 25%", "מעל הממוצע", "פעיל"
3. **Comparison Insight** - Meaningful Hebrew messages like "אתה בין ה-20% המובילים במיקוד על התאוששות השבוע"
4. **Week Distribution Chart** - Visual representation of user's direction breakdown
5. **Conditional Display** - Only shows when user has activity this week

**Backend Endpoint:**
- `GET /api/orientation/compare/{user_id}` - Returns percentile rankings and insights

**API Response includes:**
- `direction_percentiles`: Array with direction, user_count, percentile, rank_label
- `dominant_direction`: User's most frequent direction
- `dominant_percentile`: Ranking in dominant direction
- `comparison_insight`: Hebrew insight about user's position
- `week_comparison`: User's distribution as percentages

**Frontend Visualization:**
- Percentile bars for each direction with rank labels
- Week distribution mini-chart with color-coded bars
- Comparison insight text
- Header showing total actions

**Test Results:** 100% pass (23/23 backend tests, all frontend elements verified)

---

### System Logic Coherence ✅
**Status:** Complete (March 10, 2026)
- **Compass position** now calculated from **last 7 days** of actions (weighted average)
- **Recommendation engine** strictly follows theoretical balancing paths
- **Theory tab, Compass, and Recommendations** all use the **same unified model**

### Key Code Changes:
1. `recommendationService.js` - `calculateCompassPosition()` refactored to use 7-day weighted average
2. `recommendationService.js` - `calculateRecommendation()` simplified to strict theory balancing
3. `OrientationCompassSection.js` - Fixed undefined variable bug (`recommendedDirection` → `recommendedArrow`)
4. `NextBestDirectionSection.js` - Simplified to use only history for theory-based recommendations

---

## Core Product Features (December 2025)

**Status:** Complete

### 1. Theory Tab (תיאוריה)
- Created `/app/frontend/src/components/philos/sections/TheorySection.js`
- **Four Directions:** התאוששות (Recovery), סדר (Order), תרומה (Contribution), חקירה (Exploration)
- **Two Tensions:** כאוס ↔ סדר (Chaos ↔ Order), אגו ↔ קולקטיב (Ego ↔ Collective)
- **Decision Logic:** 3-step process (Actions → Patterns → Orientation)
- **Balancing Paths:** Visual mapping of negative → positive transitions
- **Hebrew intro and examples included**

### 2. Orientation Compass
- Created `/app/frontend/src/components/philos/sections/OrientationCompassSection.js`
- **Quadrant grid map** with axes:
  - Vertical: סדר (Order) ↔ כאוס (Chaos)
  - Horizontal: אגו (Ego) ↔ קולקטיב (Collective)
- **Current position indicator** with pulse animation
- **Recommended direction arrow** (dashed line)
- **Trail of recent movements** (last 7 days)
- **Empty state** for new users

### 3. Direction History with Pattern Detection
- Created `/app/frontend/src/components/philos/sections/DirectionHistorySection.js`
- **Timeframe selector:** היום (Today) | 7 ימים (7 days) | הכל (All)
- **Pattern detection** with Hebrew insights:
  - "אתה נוטה לנוע לכיוון התאוששות"
  - "יש חזרתיות בהימנעות ולאחריה סדר"
  - "נראה מעבר מתמשך לכיוון חיובי"
- **Distribution chart** showing direction percentages
- **Movement timeline** showing recent transitions

### 4. Updated Tab Navigation
- **New tab order:** בית | תובנות | מערכת | תיאוריה | היסטוריה
- Theory tab is visible and accessible (not hidden in settings)
- Compass added to Home tab
- Direction History added to Theory tab

---

## Loading Skeletons Enhancement (December 2025)

**Status:** Complete

Added lightweight loading skeletons for async components to improve perceived performance:

### New Component
- `/app/frontend/src/components/philos/LoadingSkeletons.js`
- 8 reusable skeleton components:
  - `SectionSkeleton` - Full section placeholder
  - `CardSkeleton` - Card-like content placeholder
  - `StatsSkeleton` - Statistics display placeholder
  - `ChartSkeleton` - Chart/visualization placeholder
  - `ListSkeleton` - List items placeholder
  - `InlineLoader` - Inline text replacement
  - `CollectiveSkeleton` - Specific for collective sections
  - `ReplaySkeleton` - Specific for replay insights

### Integrated Sections
- `CollectiveMirrorSection` - Uses `CollectiveSkeleton`
- `CollectiveTrajectorySection` - Uses `CollectiveSkeleton`
- `GlobalFieldSection` - Uses `SectionSkeleton`
- `ReplayInsightsSummarySection` - Uses `ReplaySkeleton` (conditional)

### Technical Details
- Consistent `animate-pulse bg-gray-200` styling
- All skeletons include `dir="rtl"` for Hebrew layout
- Minimal placeholders, no UI redesign
- Conditional rendering to prevent skeleton flash for new users

---

## Backlog

### P1 - High Priority
- [ ] Complete system stabilization pass (loading states, error handling)
- [ ] Add consistent error handling for all API requests

### P2 - Medium Priority
- [ ] Further refactor dashboard tab panel content into separate components
- [ ] Add comprehensive unit tests for services

### P3 - Future Enhancements
- [ ] Enhance Decision Path Engine with LLM integration
- [ ] Add more sophisticated collective intelligence features
- [ ] Implement user feedback loop for recommendation improvement

---

## Credentials for Testing
- **Email:** `newuser@test.com`
- **Password:** `password123`
- **Anonymous:** App automatically creates persistent anonymous user ID

---

## Last Updated
December 10, 2025 - All 4 refactoring phases completed
