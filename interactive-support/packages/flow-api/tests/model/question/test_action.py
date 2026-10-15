import pytest

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.question import (
    ActionGroup,
    ActionTextInput,
    ActionYesNo,
)


def tree() -> ActionGroup:
    return ActionGroup(
        children={
            "a": ActionTextInput(),
            "group": ActionGroup(children={"b": ActionYesNo(value="5 rue Mercière")}),
        }
    )


def test_pending_are_the_leaves_of_every_group():
    assert tree().pending() == {
        "a": ActionTextInput(),
        "b": ActionYesNo(value="5 rue Mercière"),
    }


def test_add_then_remove():
    actions = tree()

    actions.add("c", ActionTextInput())
    actions.remove("b")

    assert actions.pending() == {"a": ActionTextInput(), "c": ActionTextInput()}


def test_add_an_action_already_pending():
    with pytest.raises(InternalError, match="^ACTION_ALREADY_EXISTS:b$"):
        tree().add("b", ActionTextInput())


def test_remove_an_unknown_action():
    with pytest.raises(InternalError, match="^ACTION_NOT_FOUND:z$"):
        tree().remove("z")
