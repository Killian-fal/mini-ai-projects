import interactive_support_domain_order as orders
from interactive_support_flow_api.model.context import Extension, FlowContext
from interactive_support_flow_api.model.message import Bucket, TextCode
from interactive_support_flow_api.model.question import ChoiceQuestion
from interactive_support_flow_cancel.code import CancelCode


class CancelDeliveryModeChoice(TextCode):
    """
    The delivery modes offered to the customer: each choice's value is the orders' mode it stands for.
    """

    HOME = orders.DeliveryMode.HOME
    RELAY_POINT = orders.DeliveryMode.RELAY_POINT
    STORE = orders.DeliveryMode.STORE


class NewDeliveryMode(Extension):
    __key__ = "new_delivery_mode"

    delivery_mode: orders.DeliveryMode


def delivery_mode_choice(ctx: FlowContext) -> ChoiceQuestion[CancelDeliveryModeChoice]:
    """
    Every mode but the current one: the customer wants to change it.
    """
    order = orders.get(ctx.order_number)
    current = order.delivery_mode if order else None
    return ChoiceQuestion(
        options=[mode for mode in CancelDeliveryModeChoice if mode.value != current]
    )


def save_delivery_mode(
    ctx: FlowContext, choice: CancelDeliveryModeChoice, bucket: Bucket
) -> None:
    ctx.set_extension(NewDeliveryMode(delivery_mode=choice.value))


def update_delivery_mode(ctx: FlowContext, bucket: Bucket) -> None:
    orders.update_delivery_mode(
        ctx.order_number, ctx.require_extension(NewDeliveryMode).delivery_mode
    )
    bucket.add_code(CancelCode.DELIVERY_MODE_UPDATED)
