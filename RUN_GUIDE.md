# Windows run guide

Use PowerShell from the repository root. This is a local, single-operator prototype. The existing desktop repository is preserved; Phase 1 work is in the separate `ExtendQuality_Exasol` development copy.

## 1. Install application dependencies

Python 3.12 and Node >=22.13 are required. Start with the analytics/base environment below; it includes OpenCV and needs no trained model or paid API. Optional Ultralytics dependencies are documented in the model card.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-base.txt -r backend/requirements-exasol.txt -c backend/constraints-validated.txt
npm ci --ignore-scripts
Copy-Item .env.example .env.local
```

Do not overwrite an existing `.env.local`. Python scripts load it explicitly; Uvicorn uses `--env-file`. Never put credentials in `NEXT_PUBLIC_` variables. The optional trained-vision dependency set is large; it is not needed for the SQL demo.

## 2. Exasol Personal on Windows

Official sources checked 7 September 2026:

- [Exasol developer page](https://www.exasol.com/developers/)
- [Windows Docker quickstart](https://github.com/exasol-labs/exasol-personal-local-starterkit/blob/main/quickstarts/windows-docker.md)
- [Docker Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/)

Install and start Docker Desktop using Linux containers/WSL 2. Verify:

```powershell
wsl --version
docker info
```

The official full starter-kit entry point is:

```powershell
irm https://www.exasol.com/install/starter-kit.ps1 | iex
exakit status
```

Review the installer first. The full kit also installs data/AI tooling; this development session uses the inspected official database setup helpers to avoid unrelated MCP/client changes. Its custom container is `extendquality-exasol`, with named volume `extendquality-exasol-data`, port `127.0.0.1:8563`. Preserve the starter-kit credential file used by its read-only bind mount. The full-kit `exakit` command is available only if the full kit has been installed; Docker commands can manage this database-only setup:

```powershell
docker start extendquality-exasol
docker ps --filter name=extendquality-exasol
```

Do not use the separate launcher's `exasol install local` on Windows: its local preset documentation targets macOS. Never remove the database volume to fix a connection problem.

## 3. Configure and verify SQL

Fill `.env.local` with connection details from your installation, and set `EXASOL_ENABLED=true`. Default schema is `EQ_HACKATHON`; initializing it creates only this application's objects. Prefer trusted TLS with `EXASOL_CA_FILE`. For the loopback-only self-signed development container, `EXASOL_LOCAL_INSECURE=true` is an explicit option and is refused for remote hosts. It must not be copied into a production deployment.

```powershell
.\.venv\Scripts\python.exe scripts/exasol_admin.py health
.\.venv\Scripts\python.exe scripts/exasol_admin.py init
.\.venv\Scripts\python.exe scripts/seed_demo_data.py
.\.venv\Scripts\python.exe scripts/seed_demo_data.py --write-exasol
```

The seed preview writes nothing. Explicit seeding creates 840 synthetic demonstration records; rerunning keeps stable IDs. Real inspections are in a different source. SQL schema and queries live in `backend/database/`.

## 4. Run inspection and dashboard

The Exasol analytics demonstration works without weights: select **Synthetic demonstration data** after startup. Optional compatible local weights belong at `models/weights/bearing_real_3class.pt`; see [the model card](models/README.md). A Git clone intentionally excludes these weights and private photos. Without weights, the visual workflow reports fallback/review behavior; it cannot reproduce trained three-class inference. This distinction must also be preserved in the submission video.

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --env-file .env.local --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
npm run dev
```

Open the address printed by the frontend. `NEXT_PUBLIC_API_BASE_URL` must match the backend port; allowed origins must include the frontend address. Set these before building. Use the same hostname consistently.

Upload/capture an image, enter batch and machine IDs, run inspection, then Accept or Reject as appropriate. Phone frames initially require review; your decision changes current status, counts and history while original model evidence remains visible. The Exasol panel has separate real and synthetic source options. Check save status and pending count. Retry after database recovery:

```powershell
.\.venv\Scripts\python.exe scripts/exasol_admin.py retry
```

Each retry sends at most 100 pending inspection records and 100 review events. Repeat until pending is zero. Old SQLite-only records from before this extension are not silently imported into Exasol.

## 5. Tests and evidence

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -q
npm test
npm exec tsc -- --noEmit
.\.venv\Scripts\python.exe scripts/verify_exasol_pipeline.py
```

Tests isolate storage and force offline VLM. Default tests skip the real database test. `verify_exasol_pipeline.py` loads your local connection settings, generates an artificial image, disables model inference and exercises actual capture/review/SQL delivery using `EQ_PIPELINE_TEST`. It needs no photographs or API key. It retains the test schema for review. The historical `rehearse_demo.py` instead requires local weights and four prepared photos; it is not the fresh-clone quickstart. See [the judge walkthrough](docs/JUDGE_WALKTHROUGH.md).

## Troubleshooting

| Symptom | Diagnosis and action |
|---|---|
| Exasol unavailable | Verify Docker/container, port, credentials, TLS and initialized schema; check health; retry; never show synthetic data as fallback |
| Pending records | Inspect pending count, restore SQL connectivity, retry until zero |
| Queue failed | Inspection is local but queue write failed; inspect local disk/database before retrying capture |
| VLM offline fallback | Check provider/key/model privately; no API success is implied by a configured key |
| Phone status REVIEW | Initial safety gate; choose Accept/Reject to record final inspector decision |
| Invalid/large image | Use JPEG/PNG/WebP, <=10 MB and <=24 megapixels |
| Fresh clone cannot classify | Obtain permitted checkpoint; fallback only proposes unverified regions |

## Submission gates

The team reports that extending the pre-existing prototype is permitted for its idea submission; retain the development timeline and confirm the registered team. Add the Exasol-specific pitch deck and <=3-minute demo before marking the final package complete. The repository is prepared for separate public publication under `prajeetjoshua-hub`; original history and AI assistance provenance are retained. Track remaining deliverables in [submission/README.md](submission/README.md).

### Observed dependency constraints

`backend/constraints-validated.txt` records direct dependency versions and is not a complete transitive lock. The public setup now uses one `opencv-python` distribution, also compatible with the optional Ultralytics dependency name, rather than installing two packages into `cv2`. The fresh analytics environment is validated separately from the historical full-vision environment; see [validation](docs/VALIDATION.md).
