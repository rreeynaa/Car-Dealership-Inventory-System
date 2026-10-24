from fastapi import FastAPI

app = FastAPI(
    title="Car Dealership Inventory API",
    version="0.1.0",
    description="Manage vehicles and inventory. Interactive docs at /docs.",
)


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe used by tests, Docker, CI and the hosting platform."""
    return {"status": "ok"}