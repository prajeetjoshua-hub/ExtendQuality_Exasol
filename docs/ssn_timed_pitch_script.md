# EXtendQuality — SSN timed pitch script

Target: **4 minutes presentation + live proof**, followed by questions.

The presenter should communicate the meaning of each slide instead of reading its text. Text in quotation marks is a rehearsable script; bracketed text is stage direction.

## Before the team is called

- Start the system with `scripts/start_demo.ps1` and wait for `EXtendQuality demo is READY`.
- Run `scripts/rehearse_demo.py`. Present only after it returns `"passed": true`.
- Keep the dashboard on the primary display and `/inspection-visualizer` on the second display.
- Preselect the normal prepared image, but do not run it until the live-demo moment.
- Keep the four prepared files and the backup recording locally available.
- Assign one teammate to advance slides and one to operate the demo. The speaker must not search for files while talking.

## 0:00–0:20 — Slide 1: Position

“Good morning. We are Team ZeAI_MIH_407, and this is EXtendQuality: a local-first bearing-inspection assistant for manufacturing MSMEs. It uses fast local vision for routine evidence, asks a vision-language model for assistance only when evidence is uncertain, and always leaves the final decision with the inspector.”

[Point briefly to the three-line promise. Do not explain the photograph yet.]

## 0:20–0:50 — Slide 2: Problem

“Inspection has a difficult three-way constraint. Human judgement can vary with fatigue and lighting. Industrial defect data is scarce and expensive to curate. And sending every image to a large cloud model creates unnecessary latency, cost and privacy exposure. The opportunity is therefore not another black box—it is a governed workflow that makes uncertainty visible.”

## 0:50–1:20 — Slide 3: Architecture

“A captured frame first passes an OpenCV quality gate. A local YOLO classifier then assesses the known conditions in our current prototype. The decision engine applies explicit thresholds. Confident evidence remains local; only uncertain evidence enters the advisory VLM lane. The inspector remains the final authority, and the evidence is stored for audit and later curation.”

[Trace the five boxes from left to right, then point to the downward uncertainty branch.]

“The key economic choice is here: confident cases make no VLM API call.”

## 1:20–2:15 — Slide 4: Live dashboard

[Switch to the live dashboard.]

“Let me show one real photographed bearing passing through that workflow.”

[Run the prepared normal case. Point in this order: captured image, image-quality score, class and confidence, disposition, VLM state.]

“The frame is usable, the local model reports normal at approximately 96 percent, and the configured decision threshold recommends ACCEPT. Because the evidence is confident, the VLM is not invoked. Notice that image quality, class confidence and final disposition remain separate signals.”

[Confirm the human decision and point to the updated history or analytics.]

“The inspector’s action, model evidence and processing time are stored locally.”

## 2:15–2:40 — Slide 5: Explainability screen

[Move attention to the second screen.]

“This evidence-linked visualizer makes the route understandable at a glance. Here a rust-condition case was classified at about 77 percent and routed to REJECT locally. This screen is a presentation of stored evidence—not live 3D reconstruction and not a claim of calibrated millimetre measurement.”

## 2:40–3:10 — Slide 6: Evidence

“We also tested beyond the easiest curated views. On 33 harder excluded photographs, 31 were classified correctly: normal seven of seven, displaced seven of seven, and rust seventeen of nineteen. The two errors were rust views predicted as normal.”

“This proves prepared-workflow feasibility on the photographed bearings. It does not prove transfer to unseen bearings or production accuracy, because the present classes are correlated with only a few physical parts.”

## 3:10–3:30 — Slide 7: Cost thesis

“Our cost advantage is architectural. Routine processing uses OpenCV and YOLO locally without a per-image reasoning-model charge. Only below-threshold cases use the VLM and human review. We will not invent a rupee saving today; a pilot will measure inspection time, uncertain-case rate, false-reject cost and cloud calls per thousand parts.”

## 3:30–3:48 — Slide 8: Path to product

“The next step is a controlled pilot: measure the current baseline, standardize the camera and fixture, collect independent parts and sessions, curate reviewer-verified defects, validate per-class recall and false-accept risk, and only then deploy one assisted cell with an audit trail and rollback.”

## 3:48–4:00 — Slide 9: Ask and close

“We are asking for factory access, independent bearing samples, defect-definition support and pilot mentorship—not permission to call an unproven prototype production ready.”

“EXtendQuality is local when confident, assisted when uncertain, and human when it matters. Thank you.”

## Optional 35-second uncertain-case demonstration

Use this only if the judges ask how the VLM route works or if more demo time is explicitly offered.

[Run `6df2224d3a4c45409d6b2526b47e28c4.jpg`.]

“This view returns approximately 53 percent, below the automatic rejection threshold. The system does not hide that uncertainty. It routes to REVIEW, supplies an advisory observation through Gemini when configured—or a clearly labelled offline fallback when unavailable—and requires human confirmation. The VLM never certifies the bearing.”

## Recovery lines

### If the live UI is slow

“The first inference includes model initialization. We warm the model before normal operation; measured warm requests in our rehearsal were approximately 41 to 46 milliseconds.”

### If the camera fails

“To isolate the inspection pipeline from a camera-driver failure, I will use the same locally stored real photograph.”

### If the API or UI fails

“We have a recorded run of the identical local workflow. I will show that evidence and then answer from the architecture.”

### If Gemini is unavailable

“The routine path remains local. An uncertain inspection moves to a labelled offline fallback and human review; it never becomes an automatic acceptance.”

### If a result differs from rehearsal

“That variation is exactly why we expose the confidence and retain human authority. The prototype is demonstrating governed routing, not claiming infallibility.”

## Delivery rules

- Say **classifier** for the current three-class YOLO checkpoint; do not claim it draws defect-localization boxes.
- Say **rust condition** where grease and rust may be visually confounded.
- Say **approximately** before confidence values because retraining or preprocessing can alter them.
- Never say “100% accurate,” “production ready,” “millimetre precise,” or “the VLM decides.”
- End answers within 25 seconds unless a judge requests detail.
