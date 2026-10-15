import pytest

from interactive_support_core.handler import handle
from interactive_support_core.model import Conversation, MessageActionResponse
from interactive_support_core.opening.required_message_id import RequiredMessageId
from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.model.question import ActionGroup, ActionTextInput


def test_unknown_action_changes_nothing():
    conversation = Conversation(
        session_id="test",
        language=Language.FR,
        issue=None,
        order_number=None,
        messages=[],
        actions=ActionGroup(children={RequiredMessageId.ISSUE: ActionTextInput()}),
    )
    before = conversation.model_copy(deep=True)

    with pytest.raises(InternalError, match="^ACTION_NOT_FOUND:OPENING.ISSUE_CHOICE$"):
        handle(
            MessageActionResponse(
                action_id=RequiredMessageId.ISSUE_CHOICE, response="IssueChoice.CANCEL"
            ),
            conversation,
        )

    assert conversation == before
