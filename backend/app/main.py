from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, vehicles
from app.core.config import settings
from app.core.exceptions import OutOfStockError, VehicleNotFoundError

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
app.include_router(vehicles.router)


@app.exception_handler(VehicleNotFoundError)
async def vehicle_not_found_handler(_: Request, exc: VehicleNotFoundError) -> JSONResponse:
    """Translate the domain error into a 404 once, instead of in every route."""
    return JSONResponse(status_code=404, content={"detail": "Vehicle not found"})


@app.exception_handler(OutOfStockError)
async def out_of_stock_handler(_: Request, exc: OutOfStockError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "Vehicle is out of stock"})


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe used by tests, Docker, CI and the hosting platform."""
    return {"status": "ok"}
