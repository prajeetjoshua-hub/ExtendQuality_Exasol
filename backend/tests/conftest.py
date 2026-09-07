"""All regression tests use isolated storage and no external VLM calls."""
import os
from pathlib import Path
import tempfile

_workspace = tempfile.TemporaryDirectory(prefix="eq-tests-")
os.environ["EXTENDQUALITY_STORAGE_PATH"] = _workspace.name
os.environ["EXTENDQUALITY_DATABASE_PATH"] = str(Path(_workspace.name) / "metadata.db")
os.environ["EXTENDQUALITY_VLM_PROVIDER"] = "demo"
os.environ["YOLO_CONFIG_DIR"] = str(Path(_workspace.name) / "ultralytics")
if os.getenv("EXASOL_INTEGRATION") != "true":
    os.environ["EXASOL_ENABLED"] = "false"
