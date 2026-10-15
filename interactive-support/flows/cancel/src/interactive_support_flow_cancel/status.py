import interactive_support_domain_order as orders
from interactive_support_flow_api.model.context import FlowContext
from interactive_support_flow_api.model.message import Bucket


def order_status(ctx: FlowContext, bucket: Bucket) -> orders.OrderStatus | None:
    """
    None when the order doesn't exist: the opening only checks the number's format.
    """
    order = orders.get(ctx.order_number)
    return order.status if order else None
