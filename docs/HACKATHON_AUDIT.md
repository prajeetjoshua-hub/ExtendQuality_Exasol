# EXTEND-QUALITY HACKATHON AUDIT

Audit date: 7 September 2026. Baseline: `7c3ba5e`, 27 commits, clean original checkout. The complete laptop repository was inspected before application changes. The older `repo_patch` workspace is incomplete and was not used as the implementation baseline. Development takes place in a separate local clone; the original checkout, runtime database, secrets, and Git history remain intact.

## A. Existing features

React 19 / Next 16 via vinext/Vite; FastAPI; OpenCV image-quality checks; local Ultralytics three-class whole-image classifier; selective Gemini HTTP integration; deterministic disposition gates; camera/upload capture; human review; SQLite metadata and local raw/processed/overlay images; dashboard and evidence visualizer; prepared four-case rehearsal; prior-event slides and static GitHub Pages presentation.

| Component | Baseline classification | Evidence and limits |
|---|---|---|
| Python API, upload, history, review | WORKING | 12 baseline tests pass in isolated storage; not a production validation |
| OpenCV processing | WORKING | Decode, CLAHE, blur/exposure/contrast scoring and overlays; scores are heuristics |
| YOLO whole-image classification | PARTIALLY WORKING | Checkpoint present locally, tests run; generalization unproven |
| Gemini VLM integration | PARTIALLY WORKING | HTTP adapter and mocked tests; local key exists, values not exposed; live provider not yet revalidated |
| Decision engine | WORKING | Threshold and camera-review gates tested; no safety certification |
| React dashboard/visualizer | PARTIALLY WORKING | Complete source and controls present; fresh build validation pending at audit baseline |
| SQLite/local image persistence | WORKING | API integration tests pass; metadata must not be publicly served |
| Exasol data platform | MISSING | No driver, schema, ingestion or SQL analytics |
| Batch/machine risk and trends | MISSING | No batch/machine identity or denominator-aware quality analytics |
| Training/evaluation evidence | PARTIALLY WORKING | 77 curated views, only a few physical bearings; grease/corrosion confounding |
| Fresh-machine model/demo setup | BROKEN | Weights and four prepared samples are ignored, not delivered by a Git clone |
| Existing README/run instructions | PARTIALLY WORKING | Prior-event credits/story; base-only install omits CV packages imported at startup |
| Windows Exasol runtime | MISSING | Docker absent from PATH and standard per-user/system locations; WSL 2.6.3 with Ubuntu available |
| Submission deck/video | MISSING | Prior-event artifacts exist, but no verified Exasol submission deck or <=3-minute end-to-end demo |

## B. Working features

Preserve camera safeguards, classification semantics, explicit offline VLM labels, inspector authority, immutable model evidence, local images, and current UI. The baseline backend suite passes 12 tests. Actual frontend build, prepared inference, and post-change results are recorded in VALIDATION.md as they become available.

## C. Broken features and scientific limitations

The public static presentation is not proof of a hosted Python inference service. A fresh clone has no model weights or prepared rehearsal samples. README base-only setup cannot run imports requiring OpenCV. The API mounts all storage at `/artifacts`, exposing the SQLite file if its path is known; narrow this to processed/overlay folders. VLM JSON fields are coerced to strings, accepting malformed values; enforce nonempty bounded strings. The upload byte limit does not cap decoded pixels. UI analytics failures can leave stale values without disclosure.

The classifier does not localize balls, detect missing balls, or distinguish rust from grease. Historical 100% cross-validation is repeated views of the same physical parts, not independent-bearing accuracy. The documented 31/33 stress result includes two surface-condition false accepts and is not a new measurement from this audit. No sensor failure labels, time-to-failure target, calibrated failure probability, or industrial ROI evidence exists. Image quality is not product quality. Model confidence is not VLM confidence or calibrated defect probability.

## D. Missing Exasol components

Driver/configuration; versioned schema; immutable inspection ingestion with retry and duplicate handling; source-separated SQL aggregates; batch/machine/day views; health and analytics API; demonstrable insert-to-dashboard path; deterministic synthetic seed; database integration tests and reproducible Windows guide.

## E. Components reusable without modification

Existing visual classifier checkpoint, model limitations document, quality gates and camera review policy, visualizer, image rendering, layout, historical Git commits, and human-review workflow. Local SQLite remains a capture journal, never an Exasol substitute for hackathon analytics.

## F. Components requiring modification

Add validated batch/machine/component identity, durable local analytics outbox and explicit save status; Exasol ingestion and query modules; source filter; risk explanations; dashboard panel. Keep existing endpoints backward compatible. Restrict artifact exposure and validate model output. Extend env examples/ignores and repair reproducibility docs. New credits use only the supplied three members and mentor; historical authorship and past-event materials remain provenance.

## G. Features we should NOT build because of time

Remaining-useful-life prediction, new detector training, per-ball metrology, autonomous machine control, new Streamlit rewrite, chatbot SQL generation, cloud multi-tenancy, complex MLOps, invented performance/ROI claims. Prioritize Exasol-backed evidence and a reliable demo.

## H. Minimum viable hackathon architecture

Existing capture UI -> FastAPI/OpenCV/YOLO/selective VLM -> validated inspection -> SQLite capture journal/outbox -> Exasol Personal -> SQL batch/day aggregates -> transparent risk rules -> existing React dashboard. Outages keep inspection usable with explicit pending status; Exasol analytics return unavailable rather than local or synthetic fallback.

## I. Recommended final architecture

Keep the MVP boundaries. Store image evidence locally; only structured analytics enter Exasol. Distinguish `prototype_inspection` from `synthetic_demo` in every query. Preserve model output separately from human decision. Treat unresolved review/recapture/hold as unknown, never healthy. SQL supplies counts and rates; Python computes documented heuristic risk on SQL aggregates. Insufficient samples produce an explicit insufficient-evidence result. Risk is descriptive triage, not a prediction of failure.

## J. Estimated implementation order

1. Audit and rules/prerequisites, baseline tests (Phase 0).
2. Config, schema, driver, SQL, risk/seed unit tests (Phase 1, ~half day).
3. Durable outbox and existing dashboard integration, regression tests (~half day).
4. Docker/Exasol setup and actual SQL connectivity/seed/retry verification (~half day, host dependent).
5. Independent-bearing and live VLM evidence where available; packaging/run guide (~half day).
6. Exasol-specific deck and <=3-minute demo; clean-clone rehearsal (1–2 days).

These are estimates, not commitments or claims of completion. Innovation/impact 25%: honest industrial triage; Exasol 25%: visible ingestion and SQL; technical 20%: validation/retries/tests; UX 15%: preserve working interface; demo 10% and documentation 5%: reproducible evidence.

## Official rules and eligibility — unresolved issue

[Official event page](https://www.exasol.com/events/exasol-devjam/) checked 7 September 2026: Exasol Personal mandatory; Local/AWS/Azure; teams 3–5; deadline 13 September 2026 11:59 PM IST; public repository with deck, <=3-minute video, README and run guide. The page requires “Original work created during the hackathon window”. Existing commits begin 2 August, before registration opened 27 August. The page does not explicitly allow extending a prototype. Eligibility is UNCONFIRMED. Obtain organizer clarification before representing this extension as compliant. Preserve history and document pre-existing vs new work; do not rewrite history or remove AI provenance. Registration closed 6 September; team registration status is not verified. No extra AI-disclosure requirement was found on this page; absence is not proof that no other terms apply.

## Windows setup evidence

[Exasol Windows starter kit](https://github.com/exasol-labs/exasol-personal-local-starterkit/blob/main/quickstarts/windows-docker.md) and [developer page](https://www.exasol.com/developers/) explicitly support PowerShell + Docker Desktop, unlike the separate [Launcher local quickstart](https://docs.exasol.com/db/latest/get_started/quick_start_guide.htm), whose local preset is macOS. Use the Windows starter kit, not `exasol install local` on Windows. The unrelated starter-kit.io website is not Exasol documentation.

Measured host: Windows 11 Home build 26200, WSL 2.6.3.0/Ubuntu default version 2, hypervisor present, 8,375,230,464 bytes RAM, about 311 GB disk free, Python 3.12.14 in existing venv, Node 24.13.0. Docker not found. [Docker requirements](https://docs.docker.com/desktop/setup/install/windows-install/): WSL >=2.1.5 and 8 GB RAM; Home uses Linux containers. Memory is tight for simultaneous browser/CV/database work. Actual deployment must be tested; do not claim connectivity from prerequisites alone.

## Privacy, dependencies and provenance

No .env.local, model weights, runtime .db or .log files are tracked in the baseline. Only environment variable names were inspected from the local secret file. Local storage has 122 images per raw/processed/overlay folder plus placeholders. Original photos may contain EXIF; no private image is newly made public. Broad package ranges remain a reproducibility risk; frontend lockfile is present. Historical initial commit names Codex; preserve it. Existing framework/auth/build scaffolding is not evidence of private secrets and is not deleted just to conceal AI involvement.

Team: P Prajeet Joshua; Mohith Dharshan J; Janani Logaprabu. Mentor: Dharaniya R. Easwari Engineering College, Department of Computer Science and Engineering.

## Phase 1 disposition after implementation

Exasol client/schema/SQL/seed/outbox/review synchronization are WORKING in actual local database checks. The updated dashboard is WORKING in production build, rendered-page tests, TypeScript and side-browser inspection. Existing CV cases remain WORKING for the prepared demonstration; generalization remains unvalidated. Live Gemini returned a structured response on one prepared uncertain image. Eligibility, clean-machine model/sample distribution and final deck/video remain unresolved/MISSING. See VALIDATION.md for measured evidence and limits.

Training-script inspection confirms index-modulo photograph folds, not bearing-separated folds; the rust class comes from folders named Grease. Training starts from an experimental four-class checkpoint and runs 15 epochs on CPU; the excluded-view report ensembles three models. These scripts contain local dataset paths and remain supporting experimental material outside the submission clone. They were inspected, not rerun or modified. The prepared surface-condition photo does not independently establish corrosion; its expected class is a routing fixture, not verified ground truth.

Additional fixes: human decisions determine current status while original model evidence remains unchanged; SQLite sessions close explicitly; the frontend launcher forwards its port arguments; missing worker types were added. No provenance was removed to imply new authorship.

Read-only dataset inventory under Downloads/EXtendQuality_Dataset found 224 images in 00_raw_images, 10 in 01_annotation_trial, 224 in 02_reviewed_images, 3 in 03_exports, 59 in 04_training, 5 in 04_training_updated_2026-08-07, 5 in 05_training_4class_2026-08-07, 9 in 06_missing_ball_focused_evaluation_2026-08-07, and 287 in incoming; documents contains 14 files. These are file counts across potentially overlapping copies, not counts of distinct bearings or independently labeled examples. The dataset was not modified.
