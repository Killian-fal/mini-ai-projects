from typing import Annotated, Literal

from pydantic import BaseModel, Field

from interactive_support_api.model.action import ActionDto
from interactive_support_core.model import MessageRole


class AnswerDto(BaseModel):
    action_id: str
    # free text, a choice's key, "true"/"false", a photo as a base64 data URI,
    # or a form as a JSON object, each field's key → its value.
    response: str = Field(max_length=10_000_000)


class MessageTextDto(BaseModel):
    role: Literal[MessageRole.USER, MessageRole.ASSISTANT_GEN]
    text: str


class MessageCodeDto(BaseModel):
    role: Literal[MessageRole.ASSISTANT, MessageRole.END]
    code: str
    text: str


class MessageActionDto(BaseModel):
    role: Literal[MessageRole.ASSISTANT_ACTION]
    action_id: str
    action: ActionDto


class MessageActionResponseDto(BaseModel):
    role: Literal[MessageRole.USER_ACTION_RESPONSE]
    action_id: str
    response: str
    label: str | None


MessageDto = Annotated[
    MessageTextDto | MessageCodeDto | MessageActionDto | MessageActionResponseDto,
    Field(discriminator="role"),
]
