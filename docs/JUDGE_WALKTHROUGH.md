# Judge walkthrough

## 1. Reproduce Exasol analytics without private assets

Follow the root run guide, configure your own Exasol Personal instance, initialize the schema and run `scripts/seed_demo_data.py --write-exasol`. Start the API and dashboard. In **Batch Quality Risk**, choose **Synthetic demonstration data**.

Expected baseline: CONNECTED, 840 records, 655 accepted, 135 rejected and 50 unresolved. Three batch cards and daily trends come from Exasol SQL. Reseed and refresh: the total stays 840. This demonstrates idempotent ingestion rather than doubling the dataset.

Switch to **Real prototype inspections**. A fresh installation has zero records. That separation is intentional; simulation is not real factory evidence.

## 2. Verify capture → review → SQL

Run the deterministic integration fixture:

```powershell
.\.venv\Scripts\python.exe scripts/verify_exasol_pipeline.py
```

It generates an artificial image in memory, disables model weights and external VLM, and uses isolated local storage plus `EQ_PIPELINE_TEST`. It submits through the camera route, verifies initial REVIEW, then ACCEPT and REJECT in actual Exasol. It checks that the original REVIEW remains intact and pending delivery is zero.

This validates workflow/database behavior. The generated fixture is not a real product and proves no defect-detection accuracy. The test schema is retained for inspection and is separate from `EQ_HACKATHON`.

For an interactive demonstration, upload your own non-sensitive image. Without optional weights, inspect the explicit fallback/review message. Record an Accept/Reject decision, refresh SQL and compare the original and effective dispositions. No trained result is implied by fallback mode.

## 3. Inspect the implementation

- `backend/database/schema.sql`: original evidence, review table and effective-disposition views.
- `backend/database/queries.sql`: source-filtered SQL aggregates.
- `backend/app/db/analytics_outbox.py`: persistent delivery and retry.
- `backend/app/analytics/risk.py`: transparent risk/trend policy.
- `backend/tests/test_review_and_outbox.py`: outages and review regression tests.

## 4. Optional historical bearing model

The model card documents the local checkpoint used in earlier demonstrations. It is not included in the public repository. The analytics and generated integration fixture remain reproducible without it. A new static-product classifier, dimensional checks and physical rejection are future development, not hidden prerequisites of the SQL demonstration.
