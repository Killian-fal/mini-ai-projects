"""
Every path of the DAMAGED flow, turn by turn. `make test` checks that each transition is taken.
The orders are the seeds, reset before each test (conftest.py).
"""

import pytest

import interactive_support_domain_order as orders
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.model.flow import END
from interactive_support_flow_api.tools import llm
from interactive_support_flow_damaged import DAMAGED_FLOW
from interactive_support_flow_damaged.code import DamagedCode
from interactive_support_flow_damaged.flow import DamagedStep
from interactive_support_flow_damaged.report import ReportInput, WrittenReport
from interactive_support_flow_test import (
    Confirm,
    FlowTest,
    Photo,
    Text,
    check_flow,
    reply,
)

PHOTO = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ=="
OTHER_PHOTO = "data:image/png;base64,iVBORw0KGgo="


def order(number: str) -> orders.Order:
    found = orders.get(number)
    assert found is not None
    return found


def delivered() -> FlowTest[Photo]:
    """
    #CMA_004 is the delivered order: the photo is asked first.
    """
    return FlowTest(
        DAMAGED_FLOW,
        order_number="#CMA_004",
        language=Language.FR,
        said=[DamagedCode.ASK_PHOTO],
        next=Photo(DamagedStep.PHOTO),
    )


def test_structure():
    check_flow(DAMAGED_FLOW)


def test_unknown_order():
    FlowTest(
        DAMAGED_FLOW,
        order_number="#CMA_999",
        language=Language.FR,
        said=[DamagedCode.ORDER_NOT_FOUND],
        next=END,
    )


def test_cancelled_order():
    orders.cancel("#CMA_001", orders.Cancellation(reason="Commandée deux fois"))

    FlowTest(
        DAMAGED_FLOW,
        order_number="#CMA_001",
        language=Language.FR,
        said=[DamagedCode.ORDER_CANCELLED],
        next=END,
    )


@pytest.mark.parametrize(
    "number",
    [
        pytest.param("#CMA_001", id="not prepared"),
        pytest.param("#CMA_002", id="in preparation"),
        pytest.param("#CMA_003", id="shipped"),
    ],
)
def test_not_delivered_yet(number: str):
    FlowTest(
        DAMAGED_FLOW,
        order_number=number,
        language=Language.FR,
        said=[DamagedCode.NOT_DELIVERED_YET],
        next=END,
    )


def test_report_sent_to_support():
    report = "Le bol est fendu sur toute sa hauteur."
    before = order("#CMA_004")

    t = delivered().send_photo(
        PHOTO,
        llm=[
            reply.generate(
                ReportInput(
                    photo=llm.Image(PHOTO),
                    refused_report=None,
                    correction=None,
                    language=Language.FR,
                ),
                WrittenReport(report=report),
            )
        ],
        said=[DamagedCode.ASK_REPORT_CONFIRMATION],
        next=Confirm(DamagedStep.REPORT_CONFIRMATION, report),
    )

    t.confirm(True, said=[DamagedCode.SENT_TO_SUPPORT], next=END)

    damage = orders.Damage(photo=PHOTO, report=report)
    assert order("#CMA_004") == before.model_copy(update={"damages": (damage,)})


def test_photo_without_damage_is_asked_again():
    report = "L'écran de la lampe est déchiré sur le côté."
    before = order("#CMA_004")

    # the same question again, without its pre_hook: no second ASK_PHOTO
    t = delivered().send_photo(
        PHOTO,
        llm=[
            reply.generate(
                ReportInput(
                    photo=llm.Image(PHOTO),
                    refused_report=None,
                    correction=None,
                    language=Language.FR,
                ),
                WrittenReport(report=None),
            )
        ],
        said=[DamagedCode.NO_DAMAGE_VISIBLE],
        next=Photo(DamagedStep.PHOTO),
    )

    t = t.send_photo(
        OTHER_PHOTO,
        llm=[
            reply.generate(
                ReportInput(
                    photo=llm.Image(OTHER_PHOTO),
                    refused_report=None,
                    correction=None,
                    language=Language.FR,
                ),
                WrittenReport(report=report),
            )
        ],
        said=[DamagedCode.ASK_REPORT_CONFIRMATION],
        next=Confirm(DamagedStep.REPORT_CONFIRMATION, report),
    )

    t.confirm(True, said=[DamagedCode.SENT_TO_SUPPORT], next=END)

    damage = orders.Damage(photo=OTHER_PHOTO, report=report)
    assert order("#CMA_004") == before.model_copy(update={"damages": (damage,)})


def test_refused_report_is_corrected():
    wrong, correction, right = (
        "Le bol est fendu.",
        "C'est l'assiette qui est fendue, pas le bol",
        "L'assiette est fendue.",
    )
    before = order("#CMA_004")

    t = delivered().send_photo(
        PHOTO,
        llm=[
            reply.generate(
                ReportInput(
                    photo=llm.Image(PHOTO),
                    refused_report=None,
                    correction=None,
                    language=Language.FR,
                ),
                WrittenReport(report=wrong),
            )
        ],
        said=[DamagedCode.ASK_REPORT_CONFIRMATION],
        next=Confirm(DamagedStep.REPORT_CONFIRMATION, wrong),
    )

    t = t.confirm(
        False,
        said=[DamagedCode.ASK_REPORT_CORRECTION],
        next=Text(DamagedStep.REPORT_CORRECTION),
    )

    # the LLM gets the photo again, the refused report and the correction
    t = t.write(
        correction,
        llm=[
            reply.generate(
                ReportInput(
                    photo=llm.Image(PHOTO),
                    refused_report=wrong,
                    correction=correction,
                    language=Language.FR,
                ),
                WrittenReport(report=right),
            )
        ],
        said=[DamagedCode.ASK_REPORT_CONFIRMATION],
        next=Confirm(DamagedStep.REPORT_CONFIRMATION, right),
    )

    t.confirm(True, said=[DamagedCode.SENT_TO_SUPPORT], next=END)

    damage = orders.Damage(photo=PHOTO, report=right)
    assert order("#CMA_004") == before.model_copy(update={"damages": (damage,)})
