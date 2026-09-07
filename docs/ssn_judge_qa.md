# EXtendQuality — SSN judge Q&A

Use the first sentence as the direct answer. Add the remaining detail only if the judge stays on the topic.

## Product and differentiation

### What exactly is your product?

EXtendQuality is an assisted visual-inspection workflow for bearing manufacturers. It combines a controlled image-quality gate, a local known-condition model, explicit decision thresholds, selective VLM advice, human confirmation and traceable storage. The current build is a POC for this workflow, not a certified factory inspection machine.

### Why is this better than using Gemini for every image?

Most usable, confident inspections do not require expensive general reasoning. Local inference reduces recurring API calls, latency and unnecessary image transmission; Gemini is reserved for ambiguous evidence where an explanation or reversible next action is useful.

### Why is this better than only using YOLO?

YOLO is fast for known, represented conditions, but a confidence score does not explain every ambiguous case. The selective VLM lane can recommend actions such as clean, recapture or review while the decision engine and human remain authoritative.

### What is novel here?

The contribution is the governed combination: separate quality evidence, local known-condition inference, explicit uncertainty routing, selective reasoning, human authority and a reviewer-verified evidence loop. We are not claiming that YOLO or a VLM is individually new.

### What is your moat?

The defensible asset would be the controlled, bearing-specific evidence system and the verified dataset accumulated through pilots—not access to a generic model API. It includes capture conditions, defect definitions, reviewer agreement, model versions, decisions and outcomes.

## Accuracy and evidence

### What is your accuracy?

On 33 harder excluded views from the photographed parts, 31 were correct, or 93.94 percent. Normal was 7/7, displaced 7/7 and rust 17/19; because the images come from very few physical bearings, this is POC evidence and not unseen-bearing or production accuracy.

### Your cross-validation was 100%. Why not advertise that?

Because those folds contain repeated views of the same few physical bearings. They show that the prototype can learn those photographed conditions, but they can overestimate real deployment performance. Production validation must hold out entire bearings and capture sessions.

### What were the failures?

Two harder rust views were predicted as normal. Rust may also be confounded with brown grease because the current dataset does not independently vary bearing identity, grease and corrosion.

### How will you prevent data leakage next time?

We will assign each physical bearing and capture session a group identifier and split by those groups. No view of a held-out bearing or session will enter training, augmentation tuning or threshold selection.

### What metrics matter in production?

Per-class recall, precision, false-accept rate, false-reject rate, calibration, latency, repeatability and throughput. For safety and quality control, the false-accept rate on critical defect families is more important than headline accuracy.

### Why classify the entire image instead of localizing defects?

Whole-image classification was the fastest honest POC supported by our current labels. Product development should move to per-ball detection and geometry for count, angular spacing and radial displacement, plus verified rust-region localization.

## Bearings and manufacturing reality

### Can this inspect a sealed bearing?

It cannot see balls through an opaque shield. Ball inspection belongs before sealing in the manufacturing process; after sealing, the visible inspection scope must change to external surface conditions or use another sensing method.

### Do all bearings have eight balls?

No. Eight is the configured expectation for the photographed prototype bearings. Production rules must be selected by bearing model, and the expected geometry must come from an approved part specification.

### Can you detect a missing ball?

Not reliably with the current three-class checkpoint, and missing-ball is excluded from the present evaluation. The stronger future method is to detect each visible ball, compare the count with the model-specific expectation and evaluate angular gaps rather than drawing a box around an absence.

### Can you measure defects in millimetres?

Not from arbitrary phone photographs. Millimetre measurement requires calibrated optics, a fixed camera-to-part distance, stable fixturing, a dimensional reference and sufficient sensor resolution; the current POC reports image evidence and class confidence.

### Why use phone images at all?

They were sufficient to test software workflow feasibility quickly. A pilot must replace uncontrolled capture with fixed lighting, focus, exposure, distance, orientation and a repeatable fixture.

## VLM, safety and governance

### Does the VLM make the final decision?

No. It is advisory and is invoked only for usable but uncertain evidence. The deterministic decision state and human confirmation remain separate and stored.

### What if the VLM hallucinates?

Its output cannot automatically accept a part, and recommendations are constrained to reversible actions or review. The UI identifies the VLM route, stores its output, and keeps a human accountable.

### What happens without internet?

OpenCV, YOLO, threshold routing, local storage and the dashboard continue to work. Uncertain cases use a clearly labelled offline fallback and require review; the system does not silently claim that fallback text came from Gemini.

### How do you protect factory data?

Routine images stay local in this architecture, and VLM calls are selective. A production pilot would require consent, retention limits, access control, encryption, audit logging and a deployment-specific decision about whether uncertain images may leave the site.

### Why retain a human if the goal is automation?

Because the present evidence does not justify autonomous quality release. Human confirmation provides a safe adoption path while verified decisions create the data needed to determine whether more automation is warranted.

## Cost and venture case

### How much does it cost?

We have not validated a selling price or savings figure yet. The POC uses commodity camera/laptop hardware, local storage and no VLM charge on routine cases; the controlled pilot will measure hardware, integration, labour time, false rejects and calls per thousand inspections before pricing.

### Then how can you call it cost-effective?

We call the architecture cost-controlled, not yet economically proven. It removes a per-image reasoning-model dependency, permits a one-cell modular pilot and defines the measurements required to prove ROI against the factory baseline.

### Who pays?

The likely customer is a bearing manufacturer or MSME quality team that has a repetitive visual checkpoint and can quantify inspection labour, escapes or false rejects. The buyer and commercial model must be validated during the pilot rather than assumed from a student demo.

### What is the deployment model?

Start with one assisted inspection cell: fixed camera and lighting, an edge computer, local application and human review. Production metadata can migrate from SQLite to PostgreSQL and images to controlled object storage without changing the decision workflow.

### What is your ask from SSN?

Access to a controlled manufacturing environment, independent bearing samples, expert defect definitions and pilot mentorship. We want to turn correlated student data into defensible factory evidence.

## Scale and roadmap

### How much data do you need?

There is no defensible universal image count. We need coverage across independent physical parts, defect severities, bearing variants, capture sessions and production batches, and we stop based on validated performance and risk—not an arbitrary number of generated images.

### Will generated images solve the data problem?

They can help prototype interfaces or pretraining experiments, but they cannot substitute for independent factory evidence. Real capture and reviewer-verified defects must dominate production validation.

### How does new data enter training?

An inspection first enters a review queue. Only samples whose condition is verified by an authorized reviewer are versioned into a curated dataset; retraining is scheduled, evaluated against held-out groups and deployed only after an approval gate.

### What would a successful pilot prove?

It would show repeatable capture and acceptable per-class performance on unseen bearings while measuring throughput, false accepts, false rejects, uncertain-case rate, reviewer workload and cloud usage. A failed threshold blocks deployment rather than being hidden by an average score.

### What will you build next?

First, a fixed capture rig and independent-bearing dataset. Second, per-ball localization and bearing-specific geometry. Third, reviewer tooling, dataset versioning and deployment monitoring. Millimetre estimation comes only after camera calibration.

## High-pressure questions

### Is this just a college project with a fancy dashboard?

Today it is a deliberately bounded POC, but the dashboard is connected to a real inspection, decision and storage pipeline rather than a static mock-up. Our venture claim rests on the controlled pilot plan and measurable gates, not on visual polish alone.

### Why should we select you if the model is not production ready?

Because we have identified the real deployment risks, built a working governed architecture and defined the shortest credible experiment to reduce those risks. Support from SSN would convert the prototype’s strongest missing ingredient—independent industrial evidence—into a measured pilot.

### What stops a large vendor from copying this?

Nothing prevents copying a high-level architecture. Execution advantage must come from MSME-specific integration, low-cost deployment, bearing-domain rules, trusted factory relationships and a continuously verified dataset.

### Are you replacing inspectors?

No. The first product assists inspectors by standardizing capture, surfacing evidence and prioritizing uncertain cases. Any later reduction in manual effort must be earned through measured pilot performance and factory-approved risk thresholds.

## Answers that must never be used

- “It is 100 percent accurate.”
- “Gemini confirms whether the bearing is safe.”
- “YOLO measures the defect in millimetres.”
- “All accepted images automatically retrain the model.”
- “Every bearing has eight balls.”
- “Synthetic images are as good as factory data.”
- “We are already cheaper than industrial systems.”
