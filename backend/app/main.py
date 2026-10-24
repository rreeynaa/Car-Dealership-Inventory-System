from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth
from app.core.config import settings

app = FastAPI(
    title="Car Dealership Inventory API",
    version="0.1.0",
    description="Manage vehicles and inventory. Interactive docs at /docs.",
)

# Tokens travel in the Authorization header (not cookies), so credentials stay off.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe used by tests, Docker, CI and the hosting platform."""
    return {"status": "ok"}
