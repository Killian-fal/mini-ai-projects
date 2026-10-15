from interactive_support_core.engine import start_flow, flow_handler
from interactive_support_core.model import (
    Conversation,
    MessageActionResponse,
    MessageCode,
    MessageRole,
)
from interactive_support_core.opening.code import OpeningCode
from interactive_support_core.opening.handler import opening_handler
from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api._internal import InternalError


def handle(response: MessageActionResponse, conversation: Conversation):
    if response.action_id not in conversation.actions.pending():
        raise InternalError(f"ACTION_NOT_FOUND:{response.action_id}")
    conversation.messages.append(response)

    if conversation.context is not None:
        flow_handler(response, conversation)
    else:
        try:
            opening_handler(response, conversation)
        except InvalidAnswer as e:
            conversation.messages.append(
                MessageCode(role=MessageRole.ASSISTANT, code=e.error_code.key)
            )
            return  # the action is still pending: the same question is asked again

        if not conversation.actions.pending():
            start_flow(conversation)

    if not conversation.actions.pending():
        conversation.messages.append(
            MessageCode(
                role=MessageRole.END, code=OpeningCode.COMPLETE_CONVERSATION.key
            )
        )
