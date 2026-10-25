"""All database access for vehicles lives here (Single Responsibility)."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, func, select, update
from sqlalchemy.orm import Session

from app.models import Vehicle


@dataclass(frozen=True)
class VehicleFilters:
    """Optional search criteria. Unset fields are ignored."""

    make: str | None = None
    model: str | None = None
    category: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None


def _contains_pattern(text: str) -> str:
    """Build a LIKE pattern, escaping wildcards so user input is matched literally."""
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


class VehicleRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, vehicle: Vehicle) -> Vehicle:
        self._db.add(vehicle)
        self._db.commit()
        self._db.refresh(vehicle)
        return vehicle

    def get(self, vehicle_id: int) -> Vehicle | None:
        return self._db.get(Vehicle, vehicle_id)

    def search(self, filters: VehicleFilters, limit: int, offset: int) -> tuple[list[Vehicle], int]:
        """Return one page of matching vehicles plus the total number of matches."""
        query = self._apply_filters(select(Vehicle), filters)
        total = self._db.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = self._db.scalars(query.order_by(Vehicle.id).limit(limit).offset(offset))
        return list(rows), total

    def update(self, vehicle: Vehicle, changes: dict[str, Any]) -> Vehicle:
        for field, value in changes.items():
            setattr(vehicle, field, value)
        self._db.commit()
        self._db.refresh(vehicle)
        return vehicle

    def delete(self, vehicle: Vehicle) -> None:
        self._db.delete(vehicle)
        self._db.commit()

    def decrement_stock(self, vehicle_id: int, amount: int = 1) -> Vehicle | None:
        """Atomically remove stock. Returns None if the vehicle is missing or short on stock.

        The WHERE clause makes the check and the write one statement, so
        concurrent buyers cannot both take the last unit.
        """
        statement = (
            update(Vehicle)
            .where(Vehicle.id == vehicle_id, Vehicle.quantity >= amount)
            .values(quantity=Vehicle.quantity - amount)
            .execution_options(synchronize_session=False)
        )
        return self._apply_stock_change(statement, vehicle_id)

    def increment_stock(self, vehicle_id: int, amount: int) -> Vehicle | None:
        """Atomically add stock. Returns None if the vehicle does not exist."""
        statement = (
            update(Vehicle)
            .where(Vehicle.id == vehicle_id)
            .values(quantity=Vehicle.quantity + amount)
            .execution_options(synchronize_session=False)
        )
        return self._apply_stock_change(statement, vehicle_id)

    def _apply_stock_change(self, statement: Any, vehicle_id: int) -> Vehicle | None:
        rows_changed = self._db.execute(statement).rowcount
        self._db.commit()
        if rows_changed == 0:
            return None
        vehicle = self._db.get(Vehicle, vehicle_id)
        if vehicle is not None:
            self._db.refresh(vehicle)  # the UPDATE bypassed the ORM, so reload
        return vehicle

    @staticmethod
    def _apply_filters(query: Select, filters: VehicleFilters) -> Select:
        if filters.make:
            query = query.where(Vehicle.make.ilike(_contains_pattern(filters.make), escape="\\"))
        if filters.model:
            query = query.where(Vehicle.model.ilike(_contains_pattern(filters.model), escape="\\"))
        if filters.category:
            query = query.where(
                Vehicle.category.ilike(_contains_pattern(filters.category), escape="\\")
            )
        if filters.min_price is not None:
            query = query.where(Vehicle.price >= filters.min_price)
        if filters.max_price is not None:
            query = query.where(Vehicle.price <= filters.max_price)
        return query
