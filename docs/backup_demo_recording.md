# Offline backup demo recording

Record one 75–90 second landscape video after the final event-machine rehearsal. Its purpose is recovery: it must prove the workflow if live hardware or networking fails.

## Before recording

1. Run `powershell -ExecutionPolicy Bypass -File scripts\start_demo.ps1`.
2. Confirm it ends with `EXtendQuality demo is READY`.
3. Set browser zoom to 100%, enable Do Not Disturb and hide personal tabs.
4. Put the dashboard on display 1 and `/inspection-visualizer` on display 2.
5. Record at 1920×1080, 30 fps.

## Shot list and narration

### 0:00–0:08 — Architecture

Show the empty dashboard. “EXtendQuality is a local-first bearing inspection assistant. OpenCV validates the capture, YOLO assesses known conditions, and uncertain evidence alone enters the VLM lane.”

### 0:08–0:25 — Normal fast path

Inspect `d1c83ab19c7b467082bf513c8516d378.jpg`. “This real normal view is classified at roughly 96%. It passes the configured threshold, so the engine recommends ACCEPT without paying for or waiting on a VLM.”

### 0:25–0:42 — Known defect path

Inspect `974fdfd1b1564360a8a5c16bd648fd3c.jpg`. “All eight balls remain present, but their arrangement is abnormal. The local model returns displaced at roughly 97%, and the engine recommends REJECT.”

### 0:42–0:59 — Uncertain path

Inspect `6df2224d3a4c45409d6b2526b47e28c4.jpg`. “At roughly 53%, the evidence is below automatic rejection. The system exposes uncertainty, routes to the advisory VLM or offline fallback, and requires human confirmation.”

### 0:59–1:12 — Evidence trace

Show `/inspection-visualizer`. “The second screen presents the same stored evidence as a process trace. It is a visualization—not live 3D reconstruction and not calibrated millimetre measurement.”

### 1:12–1:25 — Close

Return to analytics and confirm a human decision. “Every inspection, timing value and reviewer decision is stored locally. Verified cases can later enter a curated retraining queue, giving MSMEs a cost-controlled path toward industrial maturity.”

## Acceptance checklist

- Text and confidence values are readable at normal playback size.
- No loading spinner, cold-start delay, notification or personal information is visible.
- The uncertain case is labelled advisory/human review.
- Never say production ready, 100% accurate or millimetre precise.
- Save `EXtendQuality_SSNDemo_Backup.mp4` on the laptop and a teammate’s drive.
