from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.inspections import router as inspections_router
from backend.app.core.config import get_settings
from backend.app.db.database import initialize_database
from backend.app.services.storage import prepare_storage
from backend.app.api.routes.analytics import router as analytics_router
from backend.app.db.analytics_outbox import initialize_outbox


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Prepare local prototype resources before the API accepts requests."""
    initialize_database()
    initialize_outbox()
    prepare_storage()
    yield


settings = get_settings()

app = FastAPI(
    title="EXtendQuality API",
    description="Bearing inspection orchestration for OpenCV, YOLO, decision logic, and VLM review.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(inspections_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
prepare_storage()
for folder in ("processed", "overlays"):
    app.mount(f"/artifacts/{folder}", StaticFiles(directory=settings.storage_path / folder), name=folder)
