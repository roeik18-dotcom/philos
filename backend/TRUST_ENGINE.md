# Trust Engine Architecture

Internal reference for the Philos Orientation V+R+T (Value + Risk + Trust) system.

## Formulas

| Concept       | Formula                                    | Notes                            |
|---------------|--------------------------------------------|----------------------------------|
| Action value  | `log(1 + impact) * authenticity`           | impact ∈ [0, ∞), auth ∈ [0, 1]  |
| Risk score    | `confidence * severity`                    | both ∈ [0, 1]                    |
| Trust score   | `value_score - risk_score`                 | Can be negative                  |
| Value decay   | `value_score *= 0.98` (daily)              | ~2% daily loss                   |
| Risk decay    | `risk_score *= 0.95` (daily)               | ~5% daily loss — risk fades faster|

## Decay Behavior

- A **CronTrigger** (APScheduler) fires at **03:00 UTC** every day.
- The job iterates every `user_state` document, multiplies scores by the decay factor, writes updated scores back, and appends a `source_flow=decay` entry to `trust_ledger`.
- **Duplicate-run protection:** A MongoDB lock document (`scheduler_locks`, `lock_id=daily_decay`) prevents:
  - Concurrent runs (checked via `running` flag).
  - Redundant scheduled runs within 23 hours (checked via `last_completed_at`).
- **Manual triggers** (`POST /api/system/decay/trigger`) bypass the 23-hour interval but still respect the concurrency lock.
- Every execution (success or failure) is logged to the `decay_log` collection.
- On deployment restart the scheduler re-initializes cleanly; `start_scheduler()` is idempotent.

## Trust Ledger

The `trust_ledger` collection is an **append-only audit log** of every event that changed a user's trust score. Each entry records:

| Field                 | Purpose                                      |
|-----------------------|----------------------------------------------|
| `source_flow`         | Where the event originated (e.g. `daily_action`, `globe_point`, `decay`, `manual`) |
| `action_type`         | Specific action (e.g. `help`, `create`, `decay`) |
| `computed_value_delta` | Change in value score                        |
| `computed_risk_delta`  | Change in risk score                         |
| `trust_score_after`    | User's trust score after this event          |
| `timestamp`            | UTC ISO timestamp                            |

## Key Collections

| Collection          | Purpose                                     |
|---------------------|---------------------------------------------|
| `user_state`        | Current scores: `value_score`, `risk_score`, `trust_score` |
| `actions`           | Raw value-producing actions                  |
| `risk_signals`      | Raw risk signals                             |
| `trust_ledger`      | Immutable audit trail                        |
| `scheduler_locks`   | Decay job lock state                         |
| `decay_log`         | Execution log for every decay run            |

## Key Endpoints

| Method | Path                                 | Auth     | Purpose                          |
|--------|--------------------------------------|----------|----------------------------------|
| POST   | `/api/actions`                       | Required | Record a value action             |
| POST   | `/api/risk-signal`                   | None     | Record a risk signal              |
| GET    | `/api/user/{user_id}/trust`          | None     | Get trust profile                 |
| GET    | `/api/user/{user_id}/trust-history`  | None     | Get full trust ledger             |
| GET    | `/api/system/status`                 | None     | System health check               |
| POST   | `/api/system/decay/trigger`          | Required | Manually trigger decay            |
