from enum import Enum

from pydantic import BaseModel, ConfigDict


class OrderStatus(Enum):
    NOT_PREPARED = "NOT_PREPARED"
    IN_PREPARATION = "IN_PREPARATION"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class DeliveryMode(Enum):
    HOME = "HOME"
    RELAY_POINT = "RELAY_POINT"
    STORE = "STORE"


class Cancellation(BaseModel):
    model_config = ConfigDict(frozen=True)

    reason: str
    details: str | None = None


class Damage(BaseModel):
    model_config = ConfigDict(frozen=True)

    photo: str
    report: str


class Order(BaseModel):
    model_config = ConfigDict(frozen=True)

    number: str
    status: OrderStatus
    address: str
    delivery_mode: DeliveryMode
    cancellation: Cancellation | None = None
    damages: tuple[Damage, ...] = ()
