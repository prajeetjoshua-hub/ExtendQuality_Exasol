# EXtendQuality — SSN claims and evidence matrix

This is the internal truth sheet for the pitch. If a claim is not supported here, qualify it or remove it.

| Pitch claim | Authoritative evidence | Status | Safe wording |
|---|---|---|---|
| The dashboard runs a real inspection pipeline. | `backend/app/services/inspection.py`, inspection API routes and the four-case rehearsal. | Proven for the local POC. | “The dashboard is connected to the working local pipeline.” |
| OpenCV assesses whether a frame is usable. | `backend/app/services/vision/preprocessor.py`; decision engine routes low-quality frames to recapture. | Proven for implemented heuristics, not all industrial conditions. | “OpenCV applies a prototype image-quality gate.” |
| YOLO classifies normal, displaced and rust conditions. | `backend/app/services/vision/detector.py`; `docs/model_evaluation.md`. | Proven for the current checkpoint and photographed samples. | “The current YOLO checkpoint is a three-class whole-image classifier.” |
| Confident routine cases avoid VLM calls. | `backend/app/services/decision/engine.py` and `backend/app/services/vlm/adapter.py`. | Proven by logic and prepared rehearsal. | “Confident cases stay local and do not invoke the VLM.” |
| Uncertain cases route to VLM or offline fallback. | Decision engine, VLM adapter and uncertain prepared case. | Proven. | “Usable, below-threshold evidence enters an advisory lane.” |
| The human is the final authority. | Review API and SQLite `human_decision`/`review_status` fields. | Proven in workflow. | “A human confirmation remains required and is stored separately.” |
| Inspections and analytics are stored locally. | `backend/app/db/database.py`, storage service and dashboard rehearsal. | Proven for SQLite plus filesystem POC. | “The POC stores metadata in SQLite and artifacts on local storage.” |
| The prepared demo covers four routes. | `scripts/rehearse_demo.py`; `docs/demo_rehearsal_2026-08-22.md`. | Proven on fixed files. | “All four prepared demo scenarios passed their expected route.” |
| Harder-view accuracy is 31/33. | `docs/model_evaluation.md`. | Proven only for the recorded excluded-view test. | “31 of 33 harder excluded photographs were correct; this is not unseen-bearing accuracy.” |
| Warm inference was 41–46 ms. | `docs/demo_rehearsal_2026-08-22.md`. | Proven for three warm requests on the event laptop. | “Warm requests in one rehearsal measured approximately 41–46 ms.” |
| The approach is cost-effective. | No completed factory cost study. Architecture avoids routine VLM calls. | Not economically proven. | “The architecture is cost-controlled; a pilot will measure ROI.” |
| The model generalizes to new bearings. | No independent-bearing holdout. | Not proven. | “Transfer to unseen bearings is the next pilot gate.” |
| Defects are localized. | Current checkpoint classifies the full image. | Not proven for current model. | “Localization is a planned product step; the current checkpoint classifies the image.” |
| Missing balls are detected. | Missing-ball class excluded from present real-photo checkpoint. | Not proven. | “Future per-ball detection will infer missing balls by model-specific count and angular gaps.” |
| Defects are measured in millimetres. | No calibrated optical fixture or pixel-to-mm conversion. | Not proven. | “The POC reports image evidence; calibrated measurement requires fixed optics and fixturing.” |
| The system is production ready. | No factory pilot, independent parts, safety validation or deployment monitoring. | Not proven. | “This is a working POC and a proposal for a controlled pilot.” |
| VLM output certifies safety. | VLM adapter is advisory and can fall back offline. | False claim. | “The VLM suggests reversible actions; it never certifies the part.” |

## Go/no-go rule for new claims

Before adding any numeric or superiority claim to the pitch, identify:

1. the exact dataset or operational population it describes;
2. the executable evaluation or stored record that produced it;
3. the denominator and failure cases;
4. whether physical parts and capture sessions were independently held out;
5. the limitation that must accompany the number.

If any item is missing, present it as a future pilot metric rather than a current result.
