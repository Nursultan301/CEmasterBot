from decimal import Decimal

from pydantic import BaseModel

from enums.commons import ShipmentStatusEnum


class ShipmentListRead(BaseModel):
    id: int
    tracking_number: str
    weight_kg: float
    declared_value: Decimal | None = Decimal("0.0")
    current_status: ShipmentStatusEnum
