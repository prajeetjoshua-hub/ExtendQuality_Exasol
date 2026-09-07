# EXtendQuality — SSN event-day checklist

## The evening before

1. Plug in the event laptop and disable sleep while connected to power.
2. Copy `EXtendQuality_SSNDemo_Backup.mp4` to the laptop and one teammate's device.
3. Put the PowerPoint, prepared images and repository on local storage; do not depend on Drive during the pitch.
4. Run the full gate:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\verify_event_readiness.ps1 -Full
   ```

5. Resolve every `[FAIL]`. A `[WARN]` about offline demo VLM mode is expected if Gemini is intentionally not configured.
6. Rehearse once with the actual presenter, operator, laptop, mouse, display adapter and screen arrangement.

## Thirty minutes before pitching

1. Connect power and the second display.
2. Enable Do Not Disturb; close email, messaging, Drive and unrelated browser tabs.
3. Set both browsers to 100% zoom.
4. Run the fast, non-destructive preflight:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\verify_event_readiness.ps1
   ```

5. Start the system:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\start_demo.ps1
   ```

6. Wait for `EXtendQuality demo is READY`.
7. Open `http://localhost:3000/` on the operator display.
8. Open `http://localhost:3000/inspection-visualizer` on the presentation display.
9. Run one non-demo warm-up image if the startup script has not already warmed the model.
10. Keep the PowerPoint and backup video open but minimized.

## Team roles

- **Lead speaker:** owns the problem, architecture, evidence, venture ask and judge answers.
- **Demo operator:** selects only the prepared files, runs inspection and confirms the human decision.
- **Slide/backup owner:** advances slides, watches elapsed time and opens the backup video if signalled.

The speaker says “show the local path” or “show uncertainty” before the operator acts. The operator never improvizes with an untested image during the primary demo.

## Demo order

1. Primary live demonstration: normal prepared case.
2. Evidence screen: stored rust trace.
3. Optional judge-requested demonstration: uncertain prepared case.
4. Displaced case is held as an additional technical proof, not required in the four-minute main flow.

## Go/no-go rules

Do not start the live demo when:

- `verify_event_readiness.ps1` reports any failure;
- `start_demo.ps1` does not print `READY`;
- the prepared result route changed after a model or preprocessing modification;
- the projector hides the confidence or disposition text;
- the operator cannot identify the prepared files without searching.

Use the backup recording immediately if a failure cannot be corrected within 15 seconds on stage. Do not debug in front of the judges.

## Physical backup bag

- Laptop charger
- Display adapter and a known-good spare cable
- Wired mouse
- Extension board
- Four physical bearings in labelled containers
- Simple non-reflective mat for the camera
- Printed one-page pitch structure and key metrics

## After the pitch

1. Record the judges' exact questions and objections.
2. Save any new inspection evidence separately; do not add it automatically to training.
3. Stop the demo cleanly:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\stop_demo.ps1
   ```

4. Preserve logs and the model version used during the demonstration.
