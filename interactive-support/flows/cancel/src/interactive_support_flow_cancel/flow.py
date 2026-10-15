"""
CANCEL flow: the customer wants to cancel an order.

Before shipping, we offer to cancel or to change the delivery instead; after shipping, we refuse.
A new address must exist: the customer confirms it on a map before it replaces the old one.
Steps that act (cancel, update) never ask a question: the asking steps before them only save the answers.
Naming: an AskStep is named after what it asks and shows `ASK_<id>`; a Step is named after its `run`.
"""

from enum import auto

from interactive_support_flow_api.model.flow import Flow, Step, AskStep, StepId, END
from interactive_support_flow_api.model.message import TextCode
from interactive_support_flow_api.model.context import Issue
from interactive_support_domain_order import OrderStatus
from interactive_support_flow_api.model.question import TextQuestion, ChoiceQuestion
from interactive_support_flow_cancel.address import (
    extract_address,
    address_form,
    find_address,
    address_confirmation,
    update_address,
)
from interactive_support_flow_cancel.cancellation import (
    save_cancel_reason,
    is_service_issue,
    apologize,
    save_service_details,
    cancel_order,
)
from interactive_support_flow_cancel.code import CancelCode
from interactive_support_flow_cancel.delivery import (
    delivery_mode_choice,
    save_delivery_mode,
    update_delivery_mode,
)
from interactive_support_flow_cancel.status import order_status


class CancelStep(StepId):
    ORDER_STATUS = auto()
    ORDER_NOT_FOUND = auto()
    ALREADY_CANCELLED = auto()
    TOO_LATE_TO_CANCEL = auto()
    PROPOSAL_NOT_PREPARED = auto()
    PROPOSAL_IN_PREPARATION = auto()
    CANCEL_REASON = auto()
    IS_SERVICE_ISSUE = auto()
    APOLOGIZE = auto()
    SERVICE_DETAILS = auto()
    CANCEL_ORDER = auto()
    NEW_ADDRESS = auto()
    ADDRESS_DETAILS = auto()
    ADDRESS_CONFIRMATION = auto()
    UPDATE_ADDRESS = auto()
    DELIVERY_MODE = auto()
    UPDATE_DELIVERY_MODE = auto()


class CancelProposal(TextCode):
    CANCEL = auto()
    CHANGE_ADDRESS = auto()
    CHANGE_DELIVERY_MODE = auto()


CANCEL_FLOW = Flow(
    issue=Issue.CANCEL,
    description="The user wants to cancel his order",
    steps=[
        Step(
            id=CancelStep.ORDER_STATUS,
            run=order_status,
            next={
                None: CancelStep.ORDER_NOT_FOUND,
                OrderStatus.NOT_PREPARED: CancelStep.PROPOSAL_NOT_PREPARED,
                OrderStatus.IN_PREPARATION: CancelStep.PROPOSAL_IN_PREPARATION,
                OrderStatus.SHIPPED: CancelStep.TOO_LATE_TO_CANCEL,
                OrderStatus.DELIVERED: CancelStep.TOO_LATE_TO_CANCEL,
                OrderStatus.CANCELLED: CancelStep.ALREADY_CANCELLED,
            },
        ),
        Step(
            id=CancelStep.ORDER_NOT_FOUND,
            run=lambda ctx, bucket: bucket.add_code(CancelCode.ORDER_NOT_FOUND),
            next=END,
        ),
        Step(
            id=CancelStep.ALREADY_CANCELLED,
            run=lambda ctx, bucket: bucket.add_code(CancelCode.ALREADY_CANCELLED),
            next=END,
        ),
        Step(
            id=CancelStep.TOO_LATE_TO_CANCEL,
            run=lambda ctx, bucket: bucket.add_code(CancelCode.TOO_LATE_TO_CANCEL),
            next=END,
        ),
        # --- Proposals: the delivery mode can only change before preparation
        AskStep(
            id=CancelStep.PROPOSAL_NOT_PREPARED,
            pre_hook=lambda ctx, bucket: bucket.add_code(CancelCode.ASK_PROPOSAL),
            question=lambda ctx: ChoiceQuestion(
                options=[
                    CancelProposal.CANCEL,
                    CancelProposal.CHANGE_ADDRESS,
                    CancelProposal.CHANGE_DELIVERY_MODE,
                ]
            ),
            next={
                CancelProposal.CANCEL: CancelStep.CANCEL_REASON,
                CancelProposal.CHANGE_ADDRESS: CancelStep.NEW_ADDRESS,
                CancelProposal.CHANGE_DELIVERY_MODE: CancelStep.DELIVERY_MODE,
            },
        ),
        AskStep(
            id=CancelStep.PROPOSAL_IN_PREPARATION,
            pre_hook=lambda ctx, bucket: bucket.add_code(CancelCode.ASK_PROPOSAL),
            question=lambda ctx: ChoiceQuestion(
                options=[CancelProposal.CANCEL, CancelProposal.CHANGE_ADDRESS]
            ),
            next={
                CancelProposal.CANCEL: CancelStep.CANCEL_REASON,
                CancelProposal.CHANGE_ADDRESS: CancelStep.NEW_ADDRESS,
            },
        ),
        # --- Cancel: a service issue gets an apology and a request for details first
        AskStep(
            id=CancelStep.CANCEL_REASON,
            pre_hook=lambda ctx, bucket: bucket.add_code(CancelCode.ASK_CANCEL_REASON),
            question=lambda ctx: TextQuestion(),
            run=save_cancel_reason,
            next=CancelStep.IS_SERVICE_ISSUE,
        ),
        Step(
            id=CancelStep.IS_SERVICE_ISSUE,
            run=is_service_issue,
            next={True: CancelStep.APOLOGIZE, False: CancelStep.CANCEL_ORDER},
        ),
        Step(id=CancelStep.APOLOGIZE, run=apologize, next=CancelStep.SERVICE_DETAILS),
        AskStep(
            id=CancelStep.SERVICE_DETAILS,
            pre_hook=lambda ctx, bucket: bucket.add_code(
                CancelCode.ASK_SERVICE_DETAILS
            ),
            question=lambda ctx: TextQuestion(),
            run=save_service_details,
            next=CancelStep.CANCEL_ORDER,
        ),
        Step(id=CancelStep.CANCEL_ORDER, run=cancel_order, next=END),
        # --- Change the address: the customer checks and completes in a form what the LLM read,
        # then confirms on a map the address found. A refused address reopens the form
        AskStep(
            id=CancelStep.NEW_ADDRESS,
            pre_hook=lambda ctx, bucket: bucket.add_code(CancelCode.ASK_NEW_ADDRESS),
            question=lambda ctx: TextQuestion(),
            run=extract_address,
            next=CancelStep.ADDRESS_DETAILS,
        ),
        AskStep(
            id=CancelStep.ADDRESS_DETAILS,
            pre_hook=lambda ctx, bucket: bucket.add_code(
                CancelCode.ASK_ADDRESS_DETAILS
            ),
            question=address_form,
            run=find_address,
            next=CancelStep.ADDRESS_CONFIRMATION,
        ),
        AskStep(
            id=CancelStep.ADDRESS_CONFIRMATION,
            pre_hook=lambda ctx, bucket: bucket.add_code(
                CancelCode.ASK_ADDRESS_CONFIRMATION
            ),
            question=address_confirmation,
            next={True: CancelStep.UPDATE_ADDRESS, False: CancelStep.ADDRESS_DETAILS},
        ),
        Step(id=CancelStep.UPDATE_ADDRESS, run=update_address, next=END),
        # --- Change the delivery mode
        AskStep(
            id=CancelStep.DELIVERY_MODE,
            pre_hook=lambda ctx, bucket: bucket.add_code(CancelCode.ASK_DELIVERY_MODE),
            question=delivery_mode_choice,
            run=save_delivery_mode,
            next=CancelStep.UPDATE_DELIVERY_MODE,
        ),
        Step(id=CancelStep.UPDATE_DELIVERY_MODE, run=update_delivery_mode, next=END),
    ],
)
