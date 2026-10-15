from enum import Enum

from interactive_support_flow_api.model.polymorphic import Polymorphic
from interactive_support_flow_api.model.question import Action


class MessageRole(Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    ASSISTANT_GEN = "ASSISTANT_GEN"
    ASSISTANT_ACTION = "ASSISTANT_ACTION"
    USER_ACTION_RESPONSE = "USER_ACTION_RESPONSE"
    END = "END"


class Message(Polymorphic):
    role: MessageRole


class MessageText(Message):
    text: str


class MessageCode(Message):
    code: str


class MessageAction(Message):
    role: MessageRole = MessageRole.ASSISTANT_ACTION
    action_id: str
    action: Action


class MessageActionResponse(Message):
    role: MessageRole = MessageRole.USER_ACTION_RESPONSE
    action_id: str
    response: str
