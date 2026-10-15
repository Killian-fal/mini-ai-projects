from enum import auto

from pydantic import Field

import interactive_support_domain_order as orders
from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.tools import llm
from interactive_support_flow_api.model.context import Extension, FlowContext
from interactive_support_flow_api.model.message import Bucket, TextCode
from interactive_support_flow_api.model.question import (
    ConfirmationQuestion,
    FormQuestion,
)
from interactive_support_flow_cancel.code import CancelCode
from interactive_support_flow_cancel import geo


class AddressField(TextCode):
    STREET = auto()
    POSTAL_CODE = auto()
    CITY = auto()


class AddressDraft(Extension):
    __key__ = "address_draft"

    street: str | None
    postal_code: str | None
    city: str | None


class NewAddress(Extension):
    __key__ = "new_address"

    address: geo.Address


class AddressInput(llm.GenerateInput):
    message: str = Field(
        description="The customer's answer when asked for their new delivery address"
    )


class ExtractedAddress(llm.GenerateOutput):
    street: str | None = Field(
        description="The number and the street of the new address, None if not given"
    )
    postal_code: str | None = Field(
        description="The postal code of the new address, None if not given"
    )
    city: str | None = Field(
        description="The city of the new address, None if not given"
    )


def extract_address(ctx: FlowContext, message: str, bucket: Bucket) -> None:
    result = llm.generate(
        "Extract each part of the new delivery address written by the customer. Never invent a part they didn't give.",
        AddressInput(message=message),
        ExtractedAddress,
    )
    if not (result.street or result.postal_code or result.city):
        raise InvalidAnswer(CancelCode.ADDRESS_UNREADABLE)
    ctx.set_extension(
        AddressDraft(
            street=result.street, postal_code=result.postal_code, city=result.city
        )
    )


def address_form(ctx: FlowContext) -> FormQuestion[AddressField]:
    """
    What the LLM read, for the customer to check and complete. After a refused address, what the customer wrote.
    """
    draft = ctx.require_extension(AddressDraft)
    return FormQuestion(
        fields=list(AddressField),
        values={
            AddressField.STREET: draft.street,
            AddressField.POSTAL_CODE: draft.postal_code,
            AddressField.CITY: draft.city,
        },
    )


def find_address(
    ctx: FlowContext, address: dict[AddressField, str], bucket: Bucket
) -> None:
    found = geo.geocode(
        f"{address[AddressField.STREET]}, {address[AddressField.POSTAL_CODE]} {address[AddressField.CITY]}"
    )
    if found is None:
        raise InvalidAnswer(CancelCode.ADDRESS_NOT_FOUND)
    ctx.set_extension(
        AddressDraft(
            street=address[AddressField.STREET],
            postal_code=address[AddressField.POSTAL_CODE],
            city=address[AddressField.CITY],
        )
    )
    ctx.set_extension(NewAddress(address=found))


def address_confirmation(ctx: FlowContext) -> ConfirmationQuestion:
    """
    The address found, on a map: the customer checks it's the right place.
    """
    address = ctx.require_extension(NewAddress).address
    return ConfirmationQuestion(value=address.label, location=address.location)


def update_address(ctx: FlowContext, bucket: Bucket) -> None:
    orders.update_address(
        ctx.order_number, ctx.require_extension(NewAddress).address.label
    )
    bucket.add_code(CancelCode.ADDRESS_UPDATED)
