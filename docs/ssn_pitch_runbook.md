# EXtendQuality — SSN Vision to Venture runbook

## One-line position

EXtendQuality is a local-first, human-governed bearing inspection assistant for MSMEs: YOLO handles routine known conditions quickly, uncertain evidence is selectively escalated to a VLM, and an inspector retains the final decision.

## What the prototype proves

- A real image can pass through an OpenCV quality gate, a local three-class YOLO classifier, explicit decision thresholds, selective VLM routing, and human confirmation.
- Normal, displaced-ball and rust/grease surface-condition samples produce
  visible evidence and a traceable disposition. The current model cannot
  separate rust from grease.
- Images, model evidence, decisions, timing and inspector confirmation are stored locally in SQLite plus filesystem storage.
- Dashboard analytics update from stored inspections.
- A second evidence-linked visualizer presents the latest result without claiming live 3D reconstruction.
- Confident cases do not call Gemini. This is the primary latency, privacy and cost-control mechanism.

The prototype does **not** prove production accuracy, millimetre measurement, all bearing variants, hidden/internal defect detection, or safe autonomous acceptance.

## Recommended four-minute speaking flow

### 0:00–0:35 — Problem

“Bearing inspection is repetitive and precision-sensitive. Existing industrial systems can be expensive to adopt, while a small manufacturer may not possess the representative defect data needed for a production model. We are not claiming to replace calibrated industrial inspection today. We are demonstrating an affordable architecture that can improve as verified factory evidence accumulates.”

### 0:35–1:05 — Differentiator

“Our system does not send every image to an expensive reasoning model. OpenCV first rejects unusable captures. A local YOLO model handles known conditions. Only uncertain, usable cases enter the VLM lane, and the human inspector remains the final authority.”

### 1:05–2:45 — Live demonstration

1. Open the inspector dashboard at `http://localhost:3000/`.
2. Choose the `6204` bearing type.
3. Select a prepared image and run inspection.
4. Point out image quality, classifier label/confidence and the separate decision result.
5. Explain whether VLM was invoked and why.
6. Confirm the human decision.
7. Show the analytics counters and recent inspection record.
8. Move the second display to `http://localhost:3000/inspection-visualizer` and show the evidence trace.

Say: “This model gives image-coordinate classification evidence. Millimetre measurement would require calibrated optics, a fixed fixture and pixel-to-millimetre conversion.”

### 2:45–3:25 — Commercial case

“The routine path runs locally on an ordinary edge computer or laptop. VLM usage is reserved for ambiguity, reducing API cost and avoiding unnecessary image transmission. Metadata stays in SQLite and images stay on local storage in this POC. A production installation can move to PostgreSQL and MinIO while retaining the same workflow.”

### 3:25–4:00 — Roadmap and close

“The next milestone is not simply more generated images. It is representative factory data across physical parts, capture sessions, bearing variants, lighting, defect severity and production batches. Reviewer-confirmed cases enter a curated queue for scheduled retraining. EXtendQuality gives MSMEs a practical path from assisted inspection to a validated product—without pretending that a student dataset is already an industrial guarantee.”

## Prepared demonstration cases

These files already exist locally under `storage/raw/`:

| Scenario | File | Expected prototype evidence | Purpose |
|---|---|---|---|
| Normal | `d1c83ab19c7b467082bf513c8516d378.jpg` | Normal around 96%, `ACCEPT`, VLM not invoked | Fast local pass |
| Displaced | `974fdfd1b1564360a8a5c16bd648fd3c.jpg` | Displaced around 97%, `REJECT`, VLM not invoked | Known defect path |
| Surface condition | `7f8e3e9a4924486a8ef38419bd878cd3.jpg` | Internal `rust` label around 77%, displayed as rust/grease surface condition, `REJECT`, VLM not invoked | Visible surface-condition path |
| Uncertain | `6df2224d3a4c45409d6b2526b47e28c4.jpg` | Displaced around 53%, `REVIEW`, selective VLM/fallback | Uncertainty and human-governance path |

Values can vary slightly only if model weights or preprocessing change. Run all four once on the hackathon laptop before presenting.

## Demo startup checklist

Open PowerShell in the repository.

Backend terminal:

```powershell
$env:YOLO_CONFIG_DIR="$PWD\.ultralytics"
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Frontend terminal:

```powershell
npm run build
npm run start
```

Verify:

- `http://127.0.0.1:8000/api/health` returns healthy.
- `http://localhost:3000/` is styled and shows the dashboard.
- `http://localhost:3000/inspection-visualizer` shows `LIVE EVIDENCE LINK`.
- Run one non-demo inspection before judges arrive to load the model into memory. The first request can take several seconds; warm requests were roughly 41–46 ms in the recorded rehearsal.
- The camera is optional; the four fixed files are the reliable primary demo.
- Keep a screen recording of all four cases as backup.
- Disable sleep, notifications and automatic updates during the pitch.

Automated rehearsal gate:

```powershell
.\.venv\Scripts\python.exe scripts\rehearse_demo.py
```

Do not begin the pitch unless it ends with `"passed": true`.

## VLM modes

- `EXTENDQUALITY_VLM_PROVIDER=demo`: safe offline fallback using measured local evidence. It is explicitly labelled as not being a visual diagnosis.
- `EXTENDQUALITY_VLM_PROVIDER=gemini`: uncertain frames call Gemini when `EXTENDQUALITY_VLM_API_KEY` is configured.
- Missing key, timeout, HTTP failure or invalid output: automatic offline fallback; inspection continues.

Never describe offline fallback text as Gemini output. Never describe VLM advice as the final quality decision.

## Cost-effectiveness argument

Do not invent a rupee figure without measured hardware, labour and API assumptions. Defend the architecture instead:

1. Local YOLO processes routine inspections without per-image API cost.
2. Selective VLM routing pays only for uncertain cases.
3. The POC uses commodity camera/laptop hardware and introduces no required cloud database.
4. Human review reduces the risk of expensive false acceptance.
5. Modular adoption lets an MSME begin with one inspection station and one defect family.

The business validation plan is to measure inspection time saved, uncertain-case rate, false reject cost and cloud calls per 1,000 inspections at a pilot factory.

## Judge Q&A

### “Is this more accurate than existing industrial inspection?”

“We have not produced evidence for that claim. The current dataset validates workflow feasibility, not industrial superiority. A controlled pilot must compare recall, false rejects, throughput and repeatability against the factory’s present inspection method.”

### “How accurate is your model?”

“On repeated views of the same few physical bearings, three-fold validation was
100%. On 33 harder excluded views, 31 were correct, or 93.94%; both errors were
surface-condition views predicted as normal. The surface class cannot yet
separate rust from grease. These are POC results, not independent-bearing
accuracy, because condition and physical part are correlated. The production
test must hold out complete bearings and capture sessions.”

### “Why use a VLM?”

“Not to replace YOLO or certify the part. It supports the uncertain lane with a grounded observation and reversible action such as clean, recapture or inspect. Known confident cases never call it.”

### “What happens without internet?”

“YOLO, OpenCV, decision logic, storage and the dashboard remain local. The uncertain case enters a labelled offline fallback and human review. The demo does not fail.”

### “Can you measure defects in millimetres?”

“Not from arbitrary phone images. That requires a fixed camera and distance, lens calibration, a known reference dimension, stable part positioning and sufficient resolution. Our POC currently works in image evidence and classification confidence.”

### “Why not add accepted inspections directly to training?”

“Operator acceptance is not automatically a correct AI label. Records first enter a reviewer-verified curation queue; only approved and versioned samples enter scheduled retraining.”

### “What about sealed bearings?”

“Ball count and displacement cannot be inspected through an opaque shield. The inspection must occur before sealing during manufacture, or the external inspection scope must change to visible surface conditions.”

### “What is the moat?”

“The long-term asset is not a generic model call. It is the curated, bearing-specific evidence loop: controlled capture, explicit geometry and thresholds, reviewer-confirmed factory data, model/version traceability and a low-cost selective reasoning architecture.”

## Claims to avoid

- “100% accurate” or “production ready.”
- “The VLM verifies safety.”
- “OpenCV removes blur.”
- “YOLO directly measures millimetres.”
- “Every saved inspection automatically trains the model.”
- “Eight balls is universal for all bearings.”
- “Generated images are equivalent to independent factory samples.”

## Final closing line

“EXtendQuality is not presenting a black-box replacement for the inspector. We are presenting a cost-controlled quality intelligence layer that knows when local evidence is strong, knows when it is uncertain, and keeps a human accountable while building the verified data needed for industrial maturity.”
