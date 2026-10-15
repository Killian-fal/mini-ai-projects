"""
DAMAGED flow: the customer's order arrived damaged.

Once delivered, the customer sends a photo: the LLM writes a damage report from it, the customer corrects it until it is right,
then it goes to the support team. Before delivery nothing can be damaged yet: we say the order is on its way.
Naming: an AskStep is named after what it asks and shows `ASK_<id>`; a Step is named after its `run`.
"""

from enum import auto

from interactive_support_domain_order import OrderStatus
from interactive_support_flow_api.model.context import Issue
from interactive_support_flow_api.model.flow import Flow, Step, AskStep, StepId, END
from interactive_support_flow_api.model.question import PhotoQuestion, TextQuestion
from interactive_support_flow_damaged.code import DamagedCode
from interactive_support_flow_damaged.report import (
    analyze_photo,
    report_confirmation,
    correct_report,
    send_to_support,
)
from interactive_support_flow_damaged.status import order_status


class DamagedStep(StepId):
    ORDER_STATUS = auto()
    ORDER_NOT_FOUND = auto()
    ORDER_CANCELLED = auto()
    NOT_DELIVERED_YET = auto()
    PHOTO = auto()
    REPORT_CONFIRMATION = auto()
    REPORT_CORRECTION = auto()
    SEND_TO_SUPPORT = auto()


DAMAGED_FLOW = Flow(
    issue=Issue.DAMAGED,
    description="The user's order was delivered damaged",
    steps=[
        Step(
            id=DamagedStep.ORDER_STATUS,
            run=order_status,
            next={
                None: DamagedStep.ORDER_NOT_FOUND,
                OrderStatus.NOT_PREPARED: DamagedStep.NOT_DELIVERED_YET,
                OrderStatus.IN_PREPARATION: DamagedStep.NOT_DELIVERED_YET,
                OrderStatus.SHIPPED: DamagedStep.NOT_DELIVERED_YET,
                OrderStatus.DELIVERED: DamagedStep.PHOTO,
                OrderStatus.CANCELLED: DamagedStep.ORDER_CANCELLED,
            },
        ),
        Step(
            id=DamagedStep.ORDER_NOT_FOUND,
            run=lambda ctx, bucket: bucket.add_code(DamagedCode.ORDER_NOT_FOUND),
            next=END,
        ),
        Step(
            id=DamagedStep.ORDER_CANCELLED,
            run=lambda ctx, bucket: bucket.add_code(DamagedCode.ORDER_CANCELLED),
            next=END,
        ),
        Step(
            id=DamagedStep.NOT_DELIVERED_YET,
            run=lambda ctx, bucket: bucket.add_code(DamagedCode.NOT_DELIVERED_YET),
            next=END,
        ),
        # --- Delivered: the report is written from the photo, then corrected until the customer confirms it
        AskStep(
            id=DamagedStep.PHOTO,
            pre_hook=lambda ctx, bucket: bucket.add_code(DamagedCode.ASK_PHOTO),
            question=lambda ctx: PhotoQuestion(),
            run=analyze_photo,
            next=DamagedStep.REPORT_CONFIRMATION,
        ),
        AskStep(
            id=DamagedStep.REPORT_CONFIRMATION,
            pre_hook=lambda ctx, bucket: bucket.add_code(
                DamagedCode.ASK_REPORT_CONFIRMATION
            ),
            question=report_confirmation,
            next={
                True: DamagedStep.SEND_TO_SUPPORT,
                False: DamagedStep.REPORT_CORRECTION,
            },
        ),
        AskStep(
            id=DamagedStep.REPORT_CORRECTION,
            pre_hook=lambda ctx, bucket: bucket.add_code(
                DamagedCode.ASK_REPORT_CORRECTION
            ),
            question=lambda ctx: TextQuestion(),
            run=correct_report,
            next=DamagedStep.REPORT_CONFIRMATION,
        ),
        Step(id=DamagedStep.SEND_TO_SUPPORT, run=send_to_support, next=END),
    ],
)
