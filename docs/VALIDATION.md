# Phase 0 / Phase 1 validation — 7 September 2026

These are measured development checks on this laptop, not factory performance claims.

| Check | Result |
|---|---|
| Original baseline backend | 12 tests passed |
| Original baseline frontend | Production build and 3 rendered-page tests passed |
| Updated backend | 26 tests passed; 1 real-database test deliberately skipped in default run |
| Actual Exasol integration | Separate real database test passed: schema, duplicate-safe insert and source separation |
| Actual capture/review/SQL pipeline | Passed: prepared image through camera route -> REVIEW -> Exasol -> human ACCEPT -> human REJECT; original REVIEW retained; pending queue 0 |
| Updated frontend | Production build, 3 rendered-page tests and TypeScript check passed |
| Four-case prepared rehearsal | All 4 passed with expected class/disposition/VLM routing |
| Live Gemini | Prepared uncertain image returned `mode=gemini`, invoked=true, nonempty observation and action |
| Dependency consistency | `pip check`: no broken requirements |
| Local browser | Dashboard visible at localhost:3010; Exasol CONNECTED and 0 pending; synthetic source displays 840 records |
| Synthetic idempotency | Repeated seed still 840 rows: 655 accepted, 135 rejected, 50 unresolved |
| Secret pattern scan | No Google/GitHub/OpenAI key-shaped strings found in tracked text files; heuristic scan is not a guarantee |
| Prepared-photo metadata | Four 640×480 JPEGs, no EXIF or GPS tags detected |
| Git identity | Prajeet Joshua / user-confirmed email matches original checkout; no commit made |

## Prepared-case evidence

| Case | Whole-image class | Model confidence | Disposition | VLM |
|---|---|---:|---|---|
| Normal | normal | 0.9615 | ACCEPT | not required |
| Displaced | displaced | 0.9689 | REJECT | not required |
| Surface condition | rust (grease/rust-confounded) | 0.7656 | REJECT | not required |
| Uncertain | displaced | 0.5299 | REVIEW | explicit offline fallback during rehearsal |

One rehearsal measured 7,265 ms for the first cold model load and roughly 29–36 ms for the next three pipeline runs. This includes local processing only, excludes Exasol commit and any live VLM latency, and is neither a benchmark nor a production latency guarantee. The separate live VLM check succeeded; the rehearsal intentionally forces offline mode.

Checkpoint SHA-256: `48a3f19f4dd1261737f32e58540eee954eede37989b95672b3286a6bc4767003`.

## Diagnose → fix → retest

- Incomplete workspace `repo_patch` lacked package manifest/history. Located full desktop repository; made an isolated clone with all 27 commits.
- Docker absent. Installed signed official Docker Desktop per-user; Docker engine 29.7.2 working. Official Exasol starter-kit database helper installed `exasol/nano:2026.2.0-nano.3-amd64` in loopback-only container `extendquality-exasol` with volume `extendquality-exasol-data`. Driver authentication succeeds despite an installer mount diagnostic warning.
- Initial schema rejected unquoted `day` alias (reserved word). Quoted it; schema initialization, seed and actual SQL integration passed.
- One test collection began before pip finished; reran after completion, all default tests passed.
- End-to-end functional assertions passed but Windows temporary cleanup failed because inherited SQLite connection contexts committed without closing. Added explicit connection close; full end-to-end script and backend suite passed afterward.
- Launcher ignored port arguments. Forwarded arguments directly to the Node CLI without a shell; preview now on localhost:3010. The dev server binds localhost/IPv6; use `localhost`, not its IPv4 address, for this frontend.
- Inherited Cloudflare type declarations were missing. Added official worker types/environment declaration and explicit response types; TypeScript passes.
- User-reported Docker login 401 does not block local engine or Exasol. Exact account error was not diagnosed. Docker sign-in is optional by default; account email verification may be relevant if sign-in is desired.

## Remaining limitations / gates

Organizer clarification of pre-existing-prototype eligibility and registration confirmation remain unresolved. No actual live phone-camera generalization test or independent-bearing evaluation was performed. The prepared camera-route test verifies workflow behavior, not camera accuracy. Fresh-machine setup is not fully complete until model/sample distribution is licensed, documented and tested on a clean machine. Existing environment used the bundled Python base with system-site packages enabled; this is not a fully clean dependency isolation test.

Exasol is currently a loopback development installation using SYS and explicit self-signed TLS allowance; migrate to a restricted application account and trusted certificate before nonlocal use. Authentication/multi-user security, concurrency/load tests and a real outage/restart drill remain future work; queue failures are tested with controlled driver failures. No SQL throughput advantage has been benchmarked.

No Exasol-specific pitch deck, final screenshots or <=3-minute submission video was produced in Phase 1. Original assets and history are retained; nothing was published, pushed, committed, or rewritten.

## Reproduce

Use RUN_GUIDE.md. Default: `python -m pytest backend/tests -q`. Actual SQL: configure the ignored environment and run `scripts/verify_exasol_pipeline.py`; it uses `EQ_PIPELINE_TEST` and isolated local storage. The publication version generates an artificial image and needs no private samples or weights. The separate `test_real_exasol_roundtrip` uses `EQ_INTEGRATION_TEST`. Both test schemas intentionally remain for inspection. Main demonstration data stays in `EQ_HACKATHON`.

## Repository publication checks — 7 September 2026

This section updates the Phase 1 baseline above. A fresh Python 3.12 virtual environment without system-site packages was created and installed using `requirements-base.txt`, `requirements-exasol.txt` and `constraints-validated.txt`. It contains one OpenCV distribution and no Ultralytics/PyTorch model dependency. `pip check` passed; the backend suite passed with 26 tests and one intentionally skipped SQL integration test. Two upstream test-client deprecation warnings remain.

The generated-fixture end-to-end script passed against actual Exasol: initial REVIEW, ACCEPT saved, REJECT saved, original REVIEW retained and pending count zero. Classification is explicitly null because model weights are disabled. This proves fresh-environment workflow/SQL reproducibility, not product detection accuracy. The frontend production build and three rendered tests passed again; TypeScript is checked separately.

The public analytics path needs no private photos, model checkpoint or paid API key. Reproducing historical trained bearing inference still needs separately permitted assets. This is a clean Python-environment check on the existing laptop, not a fresh Windows/Docker installation on another machine.

The team now reports that prototype extension is permitted for its idea submission; genuine development history remains. Public repository publication is authorized for this separate Exasol project. The Exasol pitch deck and final video remain pending and are tracked explicitly in `submission/README.md`.

A clean export containing only the prospective public files also passed the 26-test backend suite and deterministic seed preview. Its first `npm ci` exposed missing emnapi lock entries; the lock was repaired. Compatible web dependency updates reduced npm audit findings from 23 to 6. The updated clean export passed the production build, all three rendered tests and TypeScript. Remaining dependency advisories are disclosed in SECURITY.md; no zero-vulnerability claim is made.
