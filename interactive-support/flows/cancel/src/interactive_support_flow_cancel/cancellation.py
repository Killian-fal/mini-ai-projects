from pydantic import Field

import interactive_support_domain_order as orders
from interactive_support_flow_api.tools import communication, llm
from interactive_support_flow_api.model.context import Extension, FlowContext
from interactive_support_flow_api.model.message import Bucket
from interactive_support_flow_cancel.code import CancelCode


class CancelReason(Extension):
    __key__ = "cancel_reason"

    text: str


class ServiceDetails(Extension):
    __key__ = "service_details"

    text: str


class ServiceIssueApology(communication.Communication):
    __instruction__ = "Apologize for the problem the customer describes. Don't ask anything and don't say the order is cancelled: other messages follow."

    reason: str = Field(
        description="Why the customer wants to cancel their order, in their own words"
    )


SERVICE_ISSUE_QUESTION = (
    "Does the customer cancel because of a problem with our service?"
)


def save_cancel_reason(ctx: FlowContext, reason: str, bucket: Bucket) -> None:
    ctx.set_extension(CancelReason(text=reason))


def is_service_issue(ctx: FlowContext, bucket: Bucket) -> bool:
    (service_issue,) = (
        llm.classify(cancel_reason=ctx.require_extension(CancelReason).text)
        .yes_no(
            SERVICE_ISSUE_QUESTION,
            yes="Any part of the reason blames the store: the order is too slow to be prepared or shipped, an error on "
            "the website (price, stock, product page), a bad experience with support or with a previous order",
            no="Only personal reasons: changed their mind, ordered by mistake, found it cheaper elsewhere, "
            "no longer needs it, or no reason given",
        )
        .run()
    )
    return service_issue.value


def apologize(ctx: FlowContext, bucket: Bucket) -> None:
    reason = ctx.require_extension(CancelReason).text
    bucket.add_generated(
        communication.generate(ctx, ServiceIssueApology(reason=reason))
    )


def save_service_details(ctx: FlowContext, details: str, bucket: Bucket) -> None:
    ctx.set_extension(ServiceDetails(text=details))


def cancel_order(ctx: FlowContext, bucket: Bucket) -> None:
    details = ctx.get_extension(
        ServiceDetails
    )  # None when the reason isn't a service issue
    cancellation = orders.Cancellation(
        reason=ctx.require_extension(CancelReason).text,
        details=details.text if details else None,
    )
    orders.cancel(ctx.order_number, cancellation)
    bucket.add_code(CancelCode.ORDER_CANCELLED)
