"""
Every path of the CANCEL flow, turn by turn. `make test` checks that each transition is taken.
The orders are the seeds, reset before each test (conftest.py).
"""

import pytest

import interactive_support_domain_order as orders
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.model.flow import END
from interactive_support_flow_api.model.question import Location
from interactive_support_flow_cancel import CANCEL_FLOW
from interactive_support_flow_cancel.address import (
    AddressField,
    AddressInput,
    ExtractedAddress,
)
from interactive_support_flow_cancel.cancellation import (
    SERVICE_ISSUE_QUESTION,
    ServiceIssueApology,
)
from interactive_support_flow_cancel.code import CancelCode
from interactive_support_flow_cancel.delivery import CancelDeliveryModeChoice
from interactive_support_flow_cancel.flow import CancelProposal, CancelStep
from interactive_support_flow_cancel import geo
from interactive_support_flow_test import (
    Choice,
    Confirm,
    FlowTest,
    Form,
    Text,
    check_flow,
    reply,
)

PROPOSALS_NOT_PREPARED = [
    CancelProposal.CANCEL,
    CancelProposal.CHANGE_ADDRESS,
    CancelProposal.CHANGE_DELIVERY_MODE,
]
PROPOSALS_IN_PREPARATION = [CancelProposal.CANCEL, CancelProposal.CHANGE_ADDRESS]
MERCIERE = geo.Address(
    label="5 Rue Mercière 69002 Lyon",
    location=Location(latitude=45.764324, longitude=4.832535),
)
OBERKAMPF = geo.Address(
    label="18 Rue Oberkampf 75011 Paris",
    location=Location(latitude=48.863352, longitude=2.369322),
)


def order(number: str) -> orders.Order:
    found = orders.get(number)
    assert found is not None
    return found


def test_structure():
    check_flow(CANCEL_FLOW)


def test_unknown_order():
    FlowTest(
        CANCEL_FLOW,
        order_number="#CMA_999",
        language=Language.FR,
        said=[CancelCode.ORDER_NOT_FOUND],
        next=END,
    )


def test_already_cancelled():
    orders.cancel("#CMA_001", orders.Cancellation(reason="Commandée deux fois"))

    FlowTest(
        CANCEL_FLOW,
        order_number="#CMA_001",
        language=Language.FR,
        said=[CancelCode.ALREADY_CANCELLED],
        next=END,
    )


@pytest.mark.parametrize(
    "number",
    [pytest.param("#CMA_003", id="shipped"), pytest.param("#CMA_004", id="delivered")],
)
def test_too_late_once_shipped(number: str):
    FlowTest(
        CANCEL_FLOW,
        order_number=number,
        language=Language.FR,
        said=[CancelCode.TOO_LATE_TO_CANCEL],
        next=END,
    )


def test_cancel_for_a_personal_reason():
    before = order("#CMA_001")
    t = FlowTest(
        CANCEL_FLOW,
        order_number="#CMA_001",
        language=Language.FR,
        said=[CancelCode.ASK_PROPOSAL],
        next=Choice(CancelStep.PROPOSAL_NOT_PREPARED, PROPOSALS_NOT_PREPARED),
    )

    t = t.choose(
        CancelProposal.CANCEL,
        said=[CancelCode.ASK_CANCEL_REASON],
        next=Text(CancelStep.CANCEL_REASON),
    )

    t.write(
        "J'ai changé d'avis",
        llm=[
            reply.classify(
                {"cancel_reason": "J'ai changé d'avis"},
                reply.yes_no(SERVICE_ISSUE_QUESTION, False),
            )
        ],
        said=[CancelCode.ORDER_CANCELLED],
        next=END,
    )

    cancellation = orders.Cancellation(reason="J'ai changé d'avis")
    assert order("#CMA_001") == before.model_copy(
        update={"status": orders.OrderStatus.CANCELLED, "cancellation": cancellation}
    )


def test_cancel_for_a_service_issue():
    reason, details = (
        "Toujours pas préparée après 10 jours",
        "Personne ne répond au téléphone",
    )
    before = order("#CMA_002")
    t = FlowTest(
        CANCEL_FLOW,
        order_number="#CMA_002",
        language=Language.FR,
        said=[CancelCode.ASK_PROPOSAL],
        next=Choice(CancelStep.PROPOSAL_IN_PREPARATION, PROPOSALS_IN_PREPARATION),
    )

    t = t.choose(
        CancelProposal.CANCEL,
        said=[CancelCode.ASK_CANCEL_REASON],
        next=Text(CancelStep.CANCEL_REASON),
    )

    t = t.write(
        reason,
        llm=[
            reply.classify(
                {"cancel_reason": reason}, reply.yes_no(SERVICE_ISSUE_QUESTION, True)
            )
        ],
        said=[ServiceIssueApology(reason=reason), CancelCode.ASK_SERVICE_DETAILS],
        next=Text(CancelStep.SERVICE_DETAILS),
    )

    t.write(details, said=[CancelCode.ORDER_CANCELLED], next=END)

    cancellation = orders.Cancellation(reason=reason, details=details)
    assert order("#CMA_002") == before.model_copy(
        update={"status": orders.OrderStatus.CANCELLED, "cancellation": cancellation}
    )


def address_asked() -> FlowTest[Text]:
    t = FlowTest(
        CANCEL_FLOW,
        order_number="#CMA_001",
        language=Language.FR,
        said=[CancelCode.ASK_PROPOSAL],
        next=Choice(CancelStep.PROPOSAL_NOT_PREPARED, PROPOSALS_NOT_PREPARED),
    )
    return t.choose(
        CancelProposal.CHANGE_ADDRESS,
        said=[CancelCode.ASK_NEW_ADDRESS],
        next=Text(CancelStep.NEW_ADDRESS),
    )


def test_change_address(geocoded: dict[str, geo.Address | None]):
    geocoded["5 rue Mercière, 69002 Lyon"] = MERCIERE
    message = "Au 5 rue Mercière, 69002 Lyon"
    before = order("#CMA_002")
    t = FlowTest(
        CANCEL_FLOW,
        order_number="#CMA_002",
        language=Language.FR,
        said=[CancelCode.ASK_PROPOSAL],
        next=Choice(CancelStep.PROPOSAL_IN_PREPARATION, PROPOSALS_IN_PREPARATION),
    )

    t = t.choose(
        CancelProposal.CHANGE_ADDRESS,
        said=[CancelCode.ASK_NEW_ADDRESS],
        next=Text(CancelStep.NEW_ADDRESS),
    )

    t = t.write(
        message,
        llm=[
            reply.generate(
                AddressInput(message=message),
                ExtractedAddress(
                    street="5 rue Mercière", postal_code="69002", city="Lyon"
                ),
            )
        ],
        said=[CancelCode.ASK_ADDRESS_DETAILS],
        next=Form(
            CancelStep.ADDRESS_DETAILS,
            list(AddressField),
            {
                AddressField.STREET: "5 rue Mercière",
                AddressField.POSTAL_CODE: "69002",
                AddressField.CITY: "Lyon",
            },
        ),
    )

    t = t.fill(
        {
            AddressField.STREET: "5 rue Mercière",
            AddressField.POSTAL_CODE: "69002",
            AddressField.CITY: "Lyon",
        },
        said=[CancelCode.ASK_ADDRESS_CONFIRMATION],
        next=Confirm(
            CancelStep.ADDRESS_CONFIRMATION, MERCIERE.label, MERCIERE.location
        ),
    )

    t.confirm(True, said=[CancelCode.ADDRESS_UPDATED], next=END)

    assert order("#CMA_002") == before.model_copy(update={"address": MERCIERE.label})


def test_unreadable_address_is_asked_again():
    unreadable, message = "Je déménage bientôt", "8 rue Oberkampf, 75011 Paris"
    t = address_asked()

    # the same question again, without its pre_hook: no second ASK_NEW_ADDRESS
    t = t.write(
        unreadable,
        llm=[
            reply.generate(
                AddressInput(message=unreadable),
                ExtractedAddress(street=None, postal_code=None, city=None),
            )
        ],
        said=[CancelCode.ADDRESS_UNREADABLE],
        next=Text(CancelStep.NEW_ADDRESS),
    )

    t.write(
        message,
        llm=[
            reply.generate(
                AddressInput(message=message),
                ExtractedAddress(
                    street="8 rue Oberkampf", postal_code="75011", city="Paris"
                ),
            )
        ],
        said=[CancelCode.ASK_ADDRESS_DETAILS],
        next=Form(
            CancelStep.ADDRESS_DETAILS,
            list(AddressField),
            {
                AddressField.STREET: "8 rue Oberkampf",
                AddressField.POSTAL_CODE: "75011",
                AddressField.CITY: "Paris",
            },
        ),
    )


def test_the_form_completes_and_corrects_a_partial_address(
    geocoded: dict[str, geo.Address | None],
):
    geocoded["18 rue Oberkampf, 75011 Paris"] = OBERKAMPF
    message = "Je déménage au 8 rue Oberkampf à Paris"
    before = order("#CMA_001")
    t = address_asked()

    # the postal code is missing: the form shows it empty
    t = t.write(
        message,
        llm=[
            reply.generate(
                AddressInput(message=message),
                ExtractedAddress(
                    street="8 rue Oberkampf", postal_code=None, city="Paris"
                ),
            )
        ],
        said=[CancelCode.ASK_ADDRESS_DETAILS],
        next=Form(
            CancelStep.ADDRESS_DETAILS,
            list(AddressField),
            {AddressField.STREET: "8 rue Oberkampf", AddressField.CITY: "Paris"},
        ),
    )

    # the customer adds the postal code and fixes the number
    t = t.fill(
        {
            AddressField.STREET: "18 rue Oberkampf",
            AddressField.POSTAL_CODE: "75011",
            AddressField.CITY: "Paris",
        },
        said=[CancelCode.ASK_ADDRESS_CONFIRMATION],
        next=Confirm(
            CancelStep.ADDRESS_CONFIRMATION, OBERKAMPF.label, OBERKAMPF.location
        ),
    )

    t.confirm(True, said=[CancelCode.ADDRESS_UPDATED], next=END)

    assert order("#CMA_001") == before.model_copy(update={"address": OBERKAMPF.label})


def form_asked() -> FlowTest[Form[AddressField]]:
    message = "Je déménage au 8 rue Oberkampf à Paris"
    return address_asked().write(
        message,
        llm=[
            reply.generate(
                AddressInput(message=message),
                ExtractedAddress(
                    street="8 rue Oberkampf", postal_code="75011", city="Paris"
                ),
            )
        ],
        said=[CancelCode.ASK_ADDRESS_DETAILS],
        next=Form(
            CancelStep.ADDRESS_DETAILS,
            list(AddressField),
            {
                AddressField.STREET: "8 rue Oberkampf",
                AddressField.POSTAL_CODE: "75011",
                AddressField.CITY: "Paris",
            },
        ),
    )


def test_an_address_not_found_is_asked_again(geocoded: dict[str, geo.Address | None]):
    geocoded["8 rue Oberkampf, 69002 Lyon"] = None
    before = order("#CMA_001")
    t = form_asked()

    # the same form again, without its pre_hook, the order unchanged
    t.fill(
        {
            AddressField.STREET: "8 rue Oberkampf",
            AddressField.POSTAL_CODE: "69002",
            AddressField.CITY: "Lyon",
        },
        said=[CancelCode.ADDRESS_NOT_FOUND],
        next=Form(
            CancelStep.ADDRESS_DETAILS,
            list(AddressField),
            {
                AddressField.STREET: "8 rue Oberkampf",
                AddressField.POSTAL_CODE: "75011",
                AddressField.CITY: "Paris",
            },
        ),
    )

    assert order("#CMA_001") == before


def test_a_refused_address_reopens_the_form_with_what_the_customer_wrote(
    geocoded: dict[str, geo.Address | None],
):
    geocoded.update(
        {
            "18 rue Oberkampf, 75011 Paris": OBERKAMPF,
            "5 rue Mercière, 69002 Lyon": MERCIERE,
        }
    )
    before = order("#CMA_001")
    t = form_asked()

    t = t.fill(
        {
            AddressField.STREET: "18 rue Oberkampf",
            AddressField.POSTAL_CODE: "75011",
            AddressField.CITY: "Paris",
        },
        said=[CancelCode.ASK_ADDRESS_CONFIRMATION],
        next=Confirm(
            CancelStep.ADDRESS_CONFIRMATION, OBERKAMPF.label, OBERKAMPF.location
        ),
    )

    # not the right place: the form shows the customer's address, not the LLM's
    t = t.confirm(
        False,
        said=[CancelCode.ASK_ADDRESS_DETAILS],
        next=Form(
            CancelStep.ADDRESS_DETAILS,
            list(AddressField),
            {
                AddressField.STREET: "18 rue Oberkampf",
                AddressField.POSTAL_CODE: "75011",
                AddressField.CITY: "Paris",
            },
        ),
    )

    t = t.fill(
        {
            AddressField.STREET: "5 rue Mercière",
            AddressField.POSTAL_CODE: "69002",
            AddressField.CITY: "Lyon",
        },
        said=[CancelCode.ASK_ADDRESS_CONFIRMATION],
        next=Confirm(
            CancelStep.ADDRESS_CONFIRMATION, MERCIERE.label, MERCIERE.location
        ),
    )

    t.confirm(True, said=[CancelCode.ADDRESS_UPDATED], next=END)

    assert order("#CMA_001") == before.model_copy(update={"address": MERCIERE.label})


def test_change_delivery_mode():
    before = order("#CMA_001")
    t = FlowTest(
        CANCEL_FLOW,
        order_number="#CMA_001",
        language=Language.FR,
        said=[CancelCode.ASK_PROPOSAL],
        next=Choice(CancelStep.PROPOSAL_NOT_PREPARED, PROPOSALS_NOT_PREPARED),
    )

    t = t.choose(
        CancelProposal.CHANGE_DELIVERY_MODE,
        said=[CancelCode.ASK_DELIVERY_MODE],
        next=Choice(
            CancelStep.DELIVERY_MODE,
            [CancelDeliveryModeChoice.RELAY_POINT, CancelDeliveryModeChoice.STORE],
        ),
    )

    t.choose(
        CancelDeliveryModeChoice.RELAY_POINT,
        said=[CancelCode.DELIVERY_MODE_UPDATED],
        next=END,
    )

    assert order("#CMA_001") == before.model_copy(
        update={"delivery_mode": orders.DeliveryMode.RELAY_POINT}
    )
