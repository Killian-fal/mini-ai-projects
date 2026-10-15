import pytest

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.context import (
    Extension,
    FlowContext,
    Issue,
    Language,
)


class Note(Extension):
    __key__ = "note"

    text: str


class Memo(Extension):
    __key__ = "note"  # the key of Note: one of them is wrong

    text: str


def context() -> FlowContext:
    return FlowContext(
        issue=Issue.CANCEL, order_number="#CMA_001", language=Language.FR
    )


def test_extension_not_found():
    with pytest.raises(InternalError, match="^EXTENSION_NOT_FOUND:note$"):
        context().require_extension(Note)


def test_extension_key_conflict():
    ctx = context()
    ctx.set_extension(Note(text="Rappeler demain"))

    with pytest.raises(InternalError, match="^EXTENSION_KEY_CONFLICT:note$"):
        ctx.get_extension(Memo)
