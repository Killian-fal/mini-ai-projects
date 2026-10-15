"""
The LLM call of address.py, on the customer's answer when asked for their new address: `address/`, one file per kind
of answer, each case with the parts the customer gave. A part they didn't give is left out: the LLM must not invent it.
"""

import tomllib
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.context import FlowContext, Issue, Language
from interactive_support_flow_api.model.message import Bucket, GeneratedText, TextCode
from interactive_support_flow_cancel.address import AddressDraft, extract_address
from interactive_support_flow_eval import Case, evaluate


class AddressParts(BaseModel):
    # a misspelt part would silently become a None expected
    model_config = ConfigDict(extra="forbid")

    street: str | None = None
    postal_code: str | None = None
    city: str | None = None


class AddressCase(BaseModel):
    input: str
    expected: AddressParts


class Group(BaseModel):
    cases: list[AddressCase]


class NothingSaid(Bucket):
    def add_code(self, code: TextCode) -> None:
        raise AssertionError(f"EVAL_UNEXPECTED_MESSAGE:{code}")

    def add_generated(self, text: GeneratedText) -> None:
        raise AssertionError(f"EVAL_UNEXPECTED_MESSAGE:{text.text}")


def read_cases(folder: Path) -> list[Case[str, AddressParts]]:
    cases: list[Case[str, AddressParts]] = []
    for path in sorted(folder.glob("*.toml")):
        try:
            group = Group.model_validate(tomllib.loads(path.read_text()))
        except Exception as error:
            raise AssertionError(f"EVAL_CASE_INVALID:{path.name}:{error}") from None

        cases.extend(
            [
                Case(input=case.input, expected=case.expected, group=path.stem)
                for case in group.cases
            ]
        )

    return cases


def read_address(message: str) -> AddressParts:
    ctx = FlowContext(issue=Issue.CANCEL, order_number="#CMA_001", language=Language.FR)
    try:
        extract_address(ctx, message, NothingSaid())
    except InvalidAnswer:  # ADDRESS_UNREADABLE: no part read
        return AddressParts()
    draft = ctx.require_extension(AddressDraft)
    return AddressParts(
        street=draft.street, postal_code=draft.postal_code, city=draft.city
    )


def same(read: str | None, given: str | None) -> bool:
    """
    Case, commas and spaces aside: the customer checks the parts read in a form.
    """

    def normalized(part: str | None) -> str | None:
        return (
            None
            if part is None
            else " ".join(part.replace(",", " ").casefold().split())
        )

    return normalized(read) == normalized(given)


@pytest.mark.eval
def test_extract_address(request: pytest.FixtureRequest):
    evaluate(
        "cancel.extract_address",
        read_cases(request.path.parent / "address"),
        run=read_address,
        criteria={
            "street": lambda read, given: same(read.street, given.street),
            "postal_code": lambda read, given: same(
                read.postal_code, given.postal_code
            ),
            "city": lambda read, given: same(read.city, given.city),
        },
    )
