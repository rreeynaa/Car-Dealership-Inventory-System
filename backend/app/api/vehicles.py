from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.repositories.vehicle_repository import VehicleFilters, VehicleRepository
from app.schemas.vehicle import VehicleCreate, VehicleListOut, VehicleOut, VehicleUpdate
from app.services.vehicle_service import VehicleService

# Every route requires a valid token; admin-only routes add require_admin on top.
router = APIRouter(
    prefix="/api/vehicles",
    tags=["vehicles"],
    dependencies=[Depends(get_current_user)],
)
admin_only = [Depends(require_admin)]


def get_vehicle_service(db: Annotated[Session, Depends(get_db)]) -> VehicleService:
    return VehicleService(VehicleRepository(db))


ServiceDep = Annotated[VehicleService, Depends(get_vehicle_service)]
Limit = Annotated[int, Query(ge=1, le=100, description="Page size")]
Offset = Annotated[int, Query(ge=0, description="Number of items to skip")]


def _page(service: VehicleService, filters: VehicleFilters, limit: int, offset: int):
    items, total = service.search(filters, limit, offset)
    return VehicleListOut(
        items=[VehicleOut.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=VehicleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=admin_only,
)
def create_vehicle(data: VehicleCreate, service: ServiceDep):
    """Add a vehicle to the inventory (admin only)."""
    return service.create(data)


@router.get("", response_model=VehicleListOut)
def list_vehicles(service: ServiceDep, limit: Limit = 20, offset: Offset = 0):
    """List all vehicles, including out-of-stock ones, one page at a time."""
    return _page(service, VehicleFilters(), limit, offset)


@router.get("/search", response_model=VehicleListOut)
def search_vehicles(
    service: ServiceDep,
    make: Annotated[str | None, Query(max_length=100)] = None,
    model: Annotated[str | None, Query(max_length=100)] = None,
    category: Annotated[str | None, Query(max_length=50)] = None,
    min_price: Annotated[Decimal | None, Query(ge=0)] = None,
    max_price: Annotated[Decimal | None, Query(ge=0)] = None,
    limit: Limit = 20,
    offset: Offset = 0,
):
    """Search by make, model, category (partial, case-insensitive) and price range.

    Declared before /{vehicle_id} so that "search" is not parsed as an id.
    """
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(422, detail="min_price must not be greater than max_price")
    filters = VehicleFilters(
        make=make,
        model=model,
        category=category,
        min_price=min_price,
        max_price=max_price,
    )
    return _page(service, filters, limit, offset)


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, service: ServiceDep):
    return service.get(vehicle_id)


@router.put("/{vehicle_id}", response_model=VehicleOut, dependencies=admin_only)
def update_vehicle(vehicle_id: int, data: VehicleUpdate, service: ServiceDep):
    """Update a vehicle's details; send only the fields to change (admin only)."""
    return service.update(vehicle_id, data)


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=admin_only,
)
def delete_vehicle(vehicle_id: int, service: ServiceDep) -> None:
    """Delete a vehicle (admin only)."""
    service.delete(vehicle_id)
