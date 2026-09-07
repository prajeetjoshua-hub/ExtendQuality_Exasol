# Phase 1 implementation map

Baseline audit: HACKATHON_AUDIT.md. Architecture: exasol-architecture.md. Measured validation: VALIDATION.md.

| File | Change | Acceptance condition |
|---|---|---|
| backend/app/db/exasol_client.py | Validated immutable records, TLS connection boundary, sanitized failures, formatted SQL, review synchronization | Actual Exasol schema/insert/read/retry succeeds |
| backend/database/schema.sql | Inspection table, separate human decisions, effective-disposition and daily views | Re-running schema preserves records |
| backend/database/queries.sql | Source-separated overview, batch/machine, daily, category and history analytics | No mixing synthetic and prototype sources; unknowns excluded from terminal denominator |
| backend/app/analytics/risk.py | Explicit 0–100 heuristic, sample gate, descriptive trend, Wilson interval | Unit checks include empty/unknown/invalid counts and insufficient periods |
| backend/app/db/analytics_outbox.py | Durable local queue, explicit synchronization status | Outage retains records, success acknowledges after commit |
| backend/app/db/database.py | Preserve original model status; effective human status; append-only review events | Accept then Reject updates current status and counts without replacing model evidence |
| backend/app/api/routes/analytics.py | Health/query/retry API | Unavailable is explicit, no fake local fallback |
| backend/app/api/routes/inspections.py | Validated batch/machine/component form fields and review response | Old callers still work; phone decision persists |
| backend/app/services/inspection.py | Existing pipeline plus analytics enqueue | Existing four-case rehearsal preserved |
| backend/app/schemas/inspection.py | Add save status and identities | Backward-compatible response extension |
| backend/app/main.py | Add router/queue setup, restrict image mounts | Metadata/raw storage not public |
| backend/app/services/vision/preprocessor.py | Check decoded pixel budget before OpenCV allocation | Invalid/oversized image fails safely |
| backend/app/services/vlm/adapter.py | Reject blank/non-string malformed responses | Provider errors remain explicit offline fallback |
| app/inspection-dashboard.tsx | Identity controls, status after review, Exasol panel | Accept/Reject updates active result and refreshes both analytics layers |
| app/exasol-analytics.tsx | SQL source/status/counts, batch risk reasons, daily table, retries | Synthetic label visible; source change clears stale data |
| app/globals.css | Reuse industrial styling for new panel | Desktop/mobile layout inspection |
| scripts/exasol_admin.py | init, health, retry; load ignored environment | Errors sanitized, nonzero exit on failure |
| scripts/seed_demo_data.py | Fixed-seed 840 records with stable IDs | Dry-run default; explicit write flag; re-run no duplicates |
| backend/tests/test_exasol_analytics.py | Pure logic/driver boundary plus opt-in real SQL test | No secrets required for default suite |
| backend/tests/test_review_and_outbox.py | Phone review and outbox regression | Model history remains available |
| backend/tests/conftest.py | Isolated test storage and offline VLM | Tests do not contaminate live metrics |
| .env.example / .gitignore | Config placeholders; exclude credentials, databases, deployment state | No real secrets in diff |
| README.md / RUN_GUIDE.md | Honest value proposition and reproducible local steps | Clearly distinguish tested results from remaining work |
| docs/exasol-architecture.md / assets/exasol-architecture.mmd | Architecture and failure paths | Exasol role visible in pitch/demo |

## Remaining work after Phase 1

Organizer eligibility clarification and registration confirmation; model/sample distribution permission and a reproducible download/hash manifest; independent-bearing evaluation; live Gemini verification with the configured model; narrower application DB account; dedicated Exasol deck/video; final clean-machine run; external publication only when requested. Do not assign an invented license to inherited/model assets.

## Additional verified repairs

- `build/run-vinext.mjs`: forward CLI arguments directly through Node; preview port works.
- `package.json`, `package-lock.json`, `tsconfig.json`, `cloudflare-env.d.ts`: official Cloudflare types/environment declaration; TypeScript passes.
- `backend/constraints-validated.txt`: observed direct dependency versions, not a complete transitive lock.
- `scripts/verify_exasol_pipeline.py`: actual camera-route/SQL/human-review verification in a dedicated test schema.
