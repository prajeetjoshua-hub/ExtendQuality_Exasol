# EXtendQuality prototype architecture

## Scope for the SSN hackathon

The prototype demonstrates a reliable inspection workflow. It does not claim
industrial accuracy or automatic product release.

1. A camera provides a live preview.
2. The inspector captures a stable, high-resolution frame.
3. OpenCV checks focus, exposure, crop, and bearing position.
4. The current YOLO checkpoint classifies the complete image as `normal`,
   `displaced`, or `rust`.
5. The Quality Intelligence Engine evaluates image quality, class confidence,
   and configured thresholds, then returns `ACCEPT`, `REJECT`, `RECAPTURE`,
   `REVIEW`, or `SYSTEM_HOLD`.
6. Only uncertain, usable cases are sent to the advisory VLM adapter.
7. The inspector confirms the final disposition.
8. Images are stored as files; structured metadata is stored in SQLite.
9. Only separately verified records become future training candidates.

Per-ball localization, model-specific ball count, angular gaps, radial offsets,
rust-region localization, and calibrated dimensions are roadmap capabilities;
they are not outputs of the current event checkpoint.

## Frontend

The existing TypeScript application remains at the repository root to preserve
the working GitHub Pages deployment. Implemented screens:

- `/`: inspector dashboard with camera, YOLO evidence, VLM result, and analytics.
- `/inspection-visualizer`: evidence-linked presentation visualizer with an
  animated bearing and processing timeline.

## Backend

FastAPI is responsible for inspection orchestration, result storage and API
responses. The browser manages the live camera preview and submits a captured
frame. WebSocket progress events remain a future enhancement.

```text
backend/app/
  api/routes/       HTTP and WebSocket routes
  core/             environment configuration
  db/               SQLite metadata storage
  schemas/          typed request/response contracts
  services/vision/  OpenCV and YOLO
  services/decision evidence routing
  services/vlm/     grounded VLM provider adapter
```

## Data policy

- Original images are never overwritten.
- Generated images, overlays, and model weights are not committed to Git.
- An accepted production decision is not automatically a verified training label.
- A reviewer must approve a record before it enters `training_candidates`.
