"""Business rules for vehicles."""

from app.core.exceptions import VehicleNotFoundError
from app.models import Vehicle
from app.repositories.vehicle_repository import VehicleFilters, VehicleRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:
    def __init__(self, vehicles: VehicleRepository) -> None:
        self._vehicles = vehicles

    def create(self, data: VehicleCreate) -> Vehicle:
        return self._vehicles.add(Vehicle(**data.model_dump()))

    def get(self, vehicle_id: int) -> Vehicle:
        vehicle = self._vehicles.get(vehicle_id)
        if vehicle is None:
            raise VehicleNotFoundError(vehicle_id)
        return vehicle

    def search(self, filters: VehicleFilters, limit: int, offset: int) -> tuple[list[Vehicle], int]:
        return self._vehicles.search(filters, limit, offset)

    def update(self, vehicle_id: int, data: VehicleUpdate) -> Vehicle:
        vehicle = self.get(vehicle_id)
        return self._vehicles.update(vehicle, data.model_dump(exclude_unset=True))

    def delete(self, vehicle_id: int) -> None:
        self._vehicles.delete(self.get(vehicle_id))
