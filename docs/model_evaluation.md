# EXtendQuality real-photo POC evaluation

Date: 2026-08-21

## Scope

The current YOLO classification checkpoint internally classifies a complete
captured image as `normal`, `displaced`, or `rust`. Missing-ball is excluded.
The `rust` images also contain grease/staining, so the class is displayed as
**surface condition (rust / grease)** and cannot be presented as corrosion-only
detection. This is not yet an object detector that localizes every ball or a
surface-condition region.

## Curated training pool

- Normal: 17 accepted views of physical bearing C01.
- Displaced: 19 accepted views of physical bearing D01; eight balls are present but spacing/position is abnormal.
- Internal `rust` class: 41 accepted views of a grease/rust bearing across two
  capture batches; corrosion and grease are confounded.

## Three-fold repeated-view cross-validation

| Fold | Top-1 accuracy |
|---|---:|
| 1 | 100% |
| 2 | 100% |
| 3 | 100% |
| Mean | 100% |

The folds rotate chronological photographs into validation. They do not contain independent physical bearings. Therefore, 100% is repeated-view POC performance and must not be presented as industrial accuracy or expected performance on an unseen bearing.

## Excluded-view stress check

The three fold models were ensembled and evaluated on 33 lower-quality, distant, oblique or redundant views excluded during curation.

- Overall: 31/33 correct (93.94%).
- Mean confidence: 90.77%.
- Normal: 7/7 correct; recall 100%.
- Displaced: 7/7 correct; recall 100%.
- Internal `rust` / displayed surface-condition class: 17/19 correct; recall
  89.47%.
- Observed errors: two surface-condition views were predicted as normal.

## Interpretation

This evidence supports demonstration of the present workflow on the photographed bearings. It does not establish transfer to an unseen bearing. Each condition is strongly associated with one physical bearing, and rust may be confounded with heavy brown grease.

The production experiment must split by physical bearing and capture session, then report per-class recall, precision, false-accept rate, false-reject rate, calibration and latency. Ball defects should ultimately be detected per ball and checked using count, angular spacing and radial position. Rust should be localized using verified regions once independent bearings are available.
