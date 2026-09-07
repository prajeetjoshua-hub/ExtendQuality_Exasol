# EXtendQuality

EXtendQuality is an explainable, multi-level AI inspection prototype for bearing-manufacturing MSMEs. The current POC combines OpenCV image-quality checks, a local three-class YOLO whole-image classifier, a confidence-aware decision engine, selective Vision Language Model assistance, human confirmation, and traceable local storage.

The installed checkpoint internally classifies a complete photographed bearing as
`normal`, `displaced`, or `rust`. Because the current `rust` training images also
contain grease/staining, the interface honestly displays that class as **surface
condition (rust / grease)**; it does not claim to separate corrosion from
contamination. The checkpoint does **not** yet localize individual balls or
defect regions, detect missing balls, or perform calibrated dimensional
measurement. Per-ball detection and bearing-specific geometry are planned
product-development stages.

## Live demo

[Open the EXtendQuality dashboard](https://prajeetjoshua-hub.github.io/ExtendQuality/)

The presentation build is deployed directly from this repository through the
`Deploy EXtendQuality to GitHub Pages` workflow.

## Prototype interface

The current responsive inspector dashboard presents:

- Camera or prepared-image capture
- OpenCV quality evidence and YOLO classification
- Explicit disposition and selective VLM state
- Human accept/reject confirmation
- Stored analytics and recent inspection history
- A second evidence-linked visualizer at `/inspection-visualizer`

The visualizer presents the stored process trace; it is not live 3D reconstruction.

## Prototype architecture

```text
Camera / captured image
        |
        v
OpenCV image-quality gate
        |
        v
YOLO whole-image classification
        |
        v
Quality Intelligence Engine
   | confident          | uncertain
   v                    v
Decision          VLM-assisted review
   \____________________/
             |
             v
Human confirmation -> SQLite metadata + local image storage
```

The existing TypeScript application remains the frontend. The Python backend is
kept in `backend/`, while captured images and generated evidence are written to
ignored runtime folders under `storage/`.

## Run locally

```bash
npm install
npm run dev
```

Run the API in a second terminal:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r backend/requirements-base.txt
uvicorn backend.app.main:app --reload --port 8000
```

Install the larger computer-vision stack when beginning the YOLO work:

```bash
pip install -r backend/requirements-vision.txt
```

API health check: `http://127.0.0.1:8000/api/health`

Interactive API documentation: `http://127.0.0.1:8000/docs`

Day 1 inspection endpoints:

- `POST /api/inspections` uploads a captured bearing image.
- `GET /api/inspections` returns recent inspection history.
- `GET /api/inspections/{id}` returns stored evidence and decisions.
- `POST /api/inspections/{id}/review` records the inspector's accept/reject decision.

The event checkpoint is loaded from `models/weights/bearing_real_3class.pt` and
is intentionally ignored by Git. When compatible weights are absent, the API
uses OpenCV anomaly candidates and routes the result to review rather than
pretending that a defect was classified. The default VLM output is explicitly
marked as an offline fallback; it must not be presented as Gemini output or as a
final safety decision.

## Verified POC evidence

- Backend: 11 tests pass.
- Frontend: production build and 3 rendered-page tests pass.
- Prepared demonstration: normal, displaced, rust, and uncertain routes pass.
- Harder excluded photographs: 31/33 correct, with two rust views predicted as normal.

These results support demonstration of the photographed-parts workflow. They do
not establish unseen-bearing performance or production accuracy. See
`docs/model_evaluation.md` and `docs/ssn_claims_evidence_matrix.md` for scope.

## Build

```bash
npm run build
```

Team ID: `ZeAI_MIH_407`
Track: `Industry 4.0 & Manufacturing`

Team: Janani LB, Prajeet Joshua, Mohith Dharshan

## Repository map

```text
app/                      React/Next.js inspector interface
backend/app/api/          FastAPI routes
backend/app/core/         Configuration
backend/app/db/           SQLite metadata layer
backend/app/services/     OpenCV, YOLO, decision and VLM modules
backend/tests/            Backend tests
docs/                     Architecture and implementation notes
models/weights/           Local model weights (ignored by Git)
storage/                  Runtime images, overlays and metadata (ignored)
```
