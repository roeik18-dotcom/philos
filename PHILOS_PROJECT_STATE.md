# Philos Orientation – Project State (Advanced MVP)

**Last Updated:** March 10, 2026  
**Phase:** Advanced MVP Complete – Ready for Real User Testing  
**Preview:** https://orient-interpret.preview.emergentagent.com

---

## 1. System Architecture

### Tech Stack
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI
- **Backend:** FastAPI + MongoDB
- **Auth:** JWT (passlib + python-jose)
- **Sync:** localStorage + Cloud backend with caching

### Key Files
| File | Purpose | Lines |
|------|---------|-------|
| `usePhilosState.js` | Central state management | ~1180 |
| `PhilosDashboard.js` | Main dashboard with tabs | ~500 |
| `cloudSync.js` | Cloud sync + getUserId() | ~440 |
| `dataService.js` | Cached API calls | ~100 |
| `server.py` | FastAPI backend | ~2000 |
| `sections/` | 33 UI components | - |

### Data Flow
```
User Action → Backend NLP Classification → Value Tag Assignment
    ↓
Decision Storage (MongoDB) ← → localStorage Cache
    ↓
Pattern Analysis → Recommendation Engine → Calibration Layer
    ↓
Behavioral Loops (Daily/Weekly/Monthly) → User Guidance
```

---

## 2. Recommendation Engine

### Next Best Direction (6-Priority Algorithm)

| Priority | Trigger | Recommendation |
|----------|---------|----------------|
| 1 | Negative drift (harm/avoidance >40%) | Recovery or Order |
| 2 | Collective gap (>15% below average) | Gap direction |
| 3 | Replay blind spots | Unexplored direction |
| 4 | Positive momentum | Continue contribution |
| 5 | Replay preferences | Frequently replayed |
| 6 | Balance deficit | Lowest positive score |

### Follow Recommendation Flow
1. User sees "כיוון מומלץ" with direction badge
2. Clicks "פעל לפי ההמלצה" button
3. Action input prefilled + scrolled + focused
4. Indicator: "הפעולה הזו נובעת מהכיוון המומלץ"
5. Metadata saved: direction, reason, strength, followed_recommendation

### Follow-Through Analytics
- Follow rate (שיעור מעקב)
- Alignment rate (התאמת תוצאות)
- Most/least followed directions
- Pattern strength analysis

---

## 3. Calibration System

### Self-Correcting Weights
**File:** `RecommendationCalibrationSection.js`

**Formula:**
- Weights bounded: **-5 to +5**
- High alignment (>60%) → boost +1 to +5
- Low alignment (<30%) → reduce -1 to -5
- Follow rate amplifies adjustments

**Integration:**
- `calculateCalibrationWeights()` exported
- Applied as adjustment layer in `NextBestDirectionSection.js`
- New reason: "calibration_boost"
- Indicator: "משקל מכויל" when active

**Display:**
- SVG weight visualization
- Strongest (הכי מחוזק) / Weakest (מופחת)
- Hebrew insights

---

## 4. Behavioral Loops

### Hierarchy
```
Monthly (Teal) → Weekly (Purple) → Daily (Amber) → Home Navigation
```

### Daily Orientation Loop
| Field | Value |
|-------|-------|
| File | `DailyOrientationLoopSection.js` |
| Color | Amber gradient |
| Storage | `philos_daily_orientation` |
| Header | "התמצאות יומית" |
| Message | "היום מתחיל מחזור חדש של החלטות." |
| Button | "התחל את היום" |
| Metadata | day_started, orientation_direction, orientation_pattern_reference |

### Weekly Orientation Summary
| Field | Value |
|-------|-------|
| File | `WeeklyOrientationSummarySection.js` |
| Color | Purple gradient |
| Storage | `philos_weekly_orientation` |
| Header | "סיכום שבועי" |
| Message | "השבוע החדש מתחיל מתוך הדפוס של השבוע שעבר." |
| Button | "התחל את השבוע" |
| Metadata | weekId (2026-W11), weekly_orientation_direction, weekly_pattern_reference |

### Monthly Orientation
| Field | Value |
|-------|-------|
| File | `MonthlyOrientationSection.js` |
| Color | Teal/Cyan gradient |
| Storage | `philos_monthly_orientation` |
| Header | "התמצאות חודשית" |
| Message | "החודש החדש מתחיל מתוך הדפוס של החודש שעבר." |
| Button | "התחל את החודש" |
| Metadata | monthId (2026-M03), monthly_orientation_direction, monthly_pattern_reference |

---

## 5. Dashboard Structure

### Tab Navigation
```
בית (Home) | תובנות (Insights) | מערכת (System) | היסטוריה (History)
```

### Home Tab (בית)
- Monthly/Weekly/Daily Orientation (when applicable)
- **מצב היום** - Current state pattern
- **כיוון מומלץ** - Direction badge + action suggestion
- Action input + "פעל לפי ההמלצה"
- Decision result display
- Recent history (3 items)

### Insights Tab (תובנות)
- Chain Insights
- Recommendation Follow-Through
- Weekly/Monthly/Quarterly Reports
- Replay Insights Summary
- Decision Path Engine
- Path Learning
- Adaptive Learning

### System Tab (מערכת)
- Recommendation Calibration
- Replay Adaptive Effect
- Collective Mirror/Trajectory/Layer/Trends
- Global Field
- Value Constellation
- Personal/Collective Value Maps

### History Tab (היסטוריה)
- Decision History with Chains
- Decision Replay
- Decision Tree
- Decision Map
- Session Library/Comparison
- Weekly Cognitive Report
- Global Value Field/Trend
- Session Summary

---

## 6. Data Persistence & Metadata

### MongoDB Collections
| Collection | Purpose |
|------------|---------|
| `decisions` | User decisions with value tags |
| `replays` | Replay session metadata |
| `philos_user_stats` | Aggregated statistics |
| `users` | Authenticated accounts |

### Decision Schema
```javascript
{
  user_id: string,
  decision_id: string,
  parent_decision_id: string | null,
  action: string,
  decision: string,
  value_tag: "contribution|recovery|order|harm|avoidance",
  chaos_order: number,
  ego_collective: number,
  balance_score: number,
  followed_recommendation: boolean,
  recommendation_direction: string,
  recommendation_reason: string,
  recommendation_strength: number,
  timestamp: datetime
}
```

### localStorage Keys
| Key | Purpose |
|-----|---------|
| `philos_user_id` | Persistent anonymous ID |
| `philos_daily_orientation` | Daily state |
| `philos_weekly_orientation` | Weekly state |
| `philos_monthly_orientation` | Monthly state |
| `philos_history` | Local cache |

### API Caching (dataService.js)
- Collective layer: 30s TTL
- Collective trends: 60s TTL
- Promise deduplication for simultaneous calls

---

## 7. Current Project Phase

### Status: Advanced MVP Complete ✅

### Session Achievements
1. ✅ System Stabilization Pass (API caching, loading states, error handling)
2. ✅ Next Best Direction feature with 6-priority algorithm
3. ✅ Follow Recommendation action flow with metadata
4. ✅ Recommendation Follow-Through Analytics
5. ✅ Recommendation Calibration (self-correcting weights)
6. ✅ Simplified Home Mode with 4-tab navigation
7. ✅ Daily Orientation Loop
8. ✅ Weekly Orientation Summary
9. ✅ Monthly Orientation

### Test Results
| Feature | Tests | Pass Rate |
|---------|-------|-----------|
| System Stabilization | 7/7 | 100% |
| Next Best Direction | 7/7 | 100% |
| Follow Recommendation | 8/8 | 100% |
| Follow-Through Analytics | 12/12 | 100% |
| Calibration | 12/12 | 100% |
| Simplified Home Mode | 11/11 | 100% |
| Daily Orientation | 12/12 | 100% |
| Weekly Orientation | 16/16 | 100% |
| Monthly Orientation | 17/17 | 100% |

### Next Priority
- Real User Readiness Pass (onboarding, empty states, helper text)
- Refactor `usePhilosState.js` into domain-specific hooks

### Future Backlog
- Password Reset / Email Verification
- Export/Import session data
- PWA Support
- Quarterly Orientation
- LLM-enhanced path generation

---

## Test Credentials

| Type | Email | Password |
|------|-------|----------|
| Registered | newuser@test.com | password123 |
| Anonymous | Auto-generated | N/A |

---

## Component Summary (33 Sections)

### Core
- HomeNavigationSection
- ActionEvaluationSection
- DecisionHistorySection
- DecisionMapSection

### Recommendation
- NextBestDirectionSection
- RecommendationFollowThroughSection
- RecommendationCalibrationSection
- DecisionPathEngineSection

### Behavioral Loops
- DailyOrientationLoopSection
- WeeklyOrientationSummarySection
- MonthlyOrientationSection
- DailyDecisionPromptSection

### Analytics
- ChainInsightsSection
- WeeklyBehavioralReportSection
- MonthlyProgressReportSection
- QuarterlyReviewSection

### Replay
- DecisionReplaySection
- ReplayInsightsSummarySection
- ReplayAdaptiveEffectSection

### Collective
- CollectiveLayerSection
- CollectiveMirrorSection
- CollectiveTrajectorySection
- CollectiveTrendsSection
- GlobalFieldSection

### Session
- SessionSummarySection
- SessionLibrarySection
- SessionComparisonSection
- ContinuePreviousSessionSection

### Visualization
- DecisionTreeSection
- ValueConstellationSection
- PersonalMapSection
- CollectiveValueMapSection
- OrientationFieldSection

---

*Document Version: Advanced MVP*  
*Generated: March 10, 2026*
