from interactive_support_domain_order.exception import OrderError
from interactive_support_domain_order.model import (
    Order,
    OrderStatus,
    DeliveryMode,
    Cancellation,
    Damage,
)

_ORDERS: dict[str, Order] = {
    order.number: order
    for order in [
        Order(
            number="#CMA_001",
            status=OrderStatus.NOT_PREPARED,
            address="12 rue de la Paix, 75002 Paris",
            delivery_mode=DeliveryMode.HOME,
        ),
        Order(
            number="#CMA_002",
            status=OrderStatus.IN_PREPARATION,
            address="3 place Bellecour, 69002 Lyon",
            delivery_mode=DeliveryMode.RELAY_POINT,
        ),
        Order(
            number="#CMA_003",
            status=OrderStatus.SHIPPED,
            address="8 quai des Chartrons, 33000 Bordeaux",
            delivery_mode=DeliveryMode.HOME,
        ),
        Order(
            number="#CMA_004",
            status=OrderStatus.DELIVERED,
            address="21 rue Sainte-Catherine, 59000 Lille",
            delivery_mode=DeliveryMode.HOME,
        ),
    ]
}


def create(order: Order):
    if order.number in _ORDERS:
        raise OrderError(f"ORDER_ALREADY_EXISTS:{order.number}")
    _ORDERS[order.number] = order


def get(number: str) -> Order | None:
    return _ORDERS.get(number)


def update(order: Order):
    if order.number not in _ORDERS:
        raise OrderError(f"ORDER_NOT_FOUND:{order.number}")
    _ORDERS[order.number] = order


def delete(number: str):
    if number not in _ORDERS:
        raise OrderError(f"ORDER_NOT_FOUND:{number}")
    del _ORDERS[number]


def cancel(number: str, cancellation: Cancellation):
    order = _modifiable(number)
    _ORDERS[number] = order.model_copy(
        update={"status": OrderStatus.CANCELLED, "cancellation": cancellation}
    )


def update_address(number: str, address: str):
    order = _modifiable(number)
    _ORDERS[number] = order.model_copy(update={"address": address})


def update_delivery_mode(number: str, delivery_mode: DeliveryMode):
    order = _modifiable(number)
    _ORDERS[number] = order.model_copy(update={"delivery_mode": delivery_mode})


def report_damage(number: str, damage: Damage):
    order = _ORDERS.get(number)
    if order is None:
        raise OrderError(f"ORDER_NOT_FOUND:{number}")
    if order.status is not OrderStatus.DELIVERED:
        raise OrderError(f"ORDER_NOT_DELIVERED:{number}")
    _ORDERS[number] = order.model_copy(update={"damages": (*order.damages, damage)})


def _modifiable(number: str) -> Order:
    """
    An order can only be modified before it ships.
    """
    order = _ORDERS.get(number)
    if order is None:
        raise OrderError(f"ORDER_NOT_FOUND:{number}")
    if order.status not in (OrderStatus.NOT_PREPARED, OrderStatus.IN_PREPARATION):
        raise OrderError(f"ORDER_NOT_MODIFIABLE:{number}")
    return order
