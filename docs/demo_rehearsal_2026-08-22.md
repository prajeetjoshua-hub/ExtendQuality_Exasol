# SSN demo rehearsal evidence — 2026-08-22

The four prepared images were processed in one isolated database/storage session using `bearing_real_3class.pt` and offline VLM fallback mode.

| Scenario | Classification | Confidence | Disposition | VLM route | Processing time |
|---|---|---:|---|---|---:|
| Normal | normal | 96.15% | ACCEPT | not required | 7,822.32 ms cold start |
| Displaced | displaced | 96.89% | REJECT | not required | 46.33 ms |
| Rust | rust | 76.56% | REJECT | not required | 44.55 ms |
| Uncertain | displaced | 52.99% | REVIEW | offline fallback | 41.37 ms |

Result: **4/4 prepared demo scenarios passed their expected pipeline route.**

Stored-session summary:

- Total: 4
- ACCEPT: 1
- REJECT: 2
- REVIEW: 1
- Class counts: normal 1, displaced 2, rust 1
- Pending human confirmation: 4

The first request includes one-time model initialization and must not be quoted as steady-state inference latency. The measured warm requests in this run were 41–46 ms. Before the presentation, run one non-demo image to warm the model and then reset or ignore that warm-up record in the dashboard.

This is a deterministic prepared-case rehearsal, not an independent accuracy evaluation. See `docs/model_evaluation.md` for evaluation scope and limitations.
