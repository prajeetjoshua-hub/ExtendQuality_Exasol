# Analytics method

## Unit of analysis

One record represents an inspection event, not necessarily a distinct component. Repeated photographs of a component can produce multiple events. Use component IDs and an independently designed sampling plan before interpreting rates as production prevalence.

The query always selects either `prototype_inspection` or `synthetic_demo`. Those sources are never pooled implicitly. Original model evidence is immutable; a later human Accept/Reject decision determines the effective disposition.

## Rates and risk policy

Let N be all records, E be effective ACCEPT/REJECT records and R be effective REJECT records.

- Rejection rate = R / E. With E = 0 it is unknown.
- Unresolved rate = (N − E) / N. With N = 0 it is unknown.
- At least 20 terminal dispositions are required to assign a triage score.
- Score = 100 × (0.8 × rejection rate + 0.2 × unresolved rate).
- LOW: score < 20; ELEVATED: 20 ≤ score < 40; HIGH: score ≥ 40.

These weights, sample threshold and cutoffs are **uncalibrated demonstration policy**. LOW does not certify a batch. An unresolved case is not treated as healthy.

The displayed Wilson 95% interval assumes independent binary observations; repeated views of a bearing violate that assumption. It is not a confidence interval for an independently verified factory defect rate.

## Trend

Compare the last two observed UTC dates when each has at least 20 eligible dispositions. A change above +5 percentage points is rising; below −5 is falling; otherwise stable. Missing dates are not imputed. This is a retrospective comparison, not a forecast.

## Demonstration dataset

`scripts/seed_demo_data.py` deterministically creates 3 batches × 7 days × 40 events = 840 synthetic records. Seed 20260907 yields 655 ACCEPT, 135 REJECT and 50 REVIEW records. IDs are stable, so repeated writes are idempotent. Category names retain the historical bearing demonstration; they do not show a static-product model has been trained.

The generator invokes no image classifier or VLM. Its image-quality value and processing fields are simulated placeholders, not measured performance. Model confidence is absent. Read the code to inspect the generating assumptions; do not infer industrial performance from the resulting curves.

## Excluded claims

No predicted failure date, remaining useful life, calibrated failure probability, automatic root-cause finding, proven corrosion diagnosis, certified dimensional measurement or guaranteed return on investment is implemented.
