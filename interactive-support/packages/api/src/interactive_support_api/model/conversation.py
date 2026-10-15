from pydantic import BaseModel, Field

from interactive_support_api.model.message import MessageDto
from interactive_support_flow_api.model.context import Language


class StartConversationDto(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ConversationDto(BaseModel):
    id: str
    language: Language
    messages: list[MessageDto]
