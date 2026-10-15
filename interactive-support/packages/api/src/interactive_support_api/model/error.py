from pydantic import BaseModel


class ErrorDto(BaseModel):
    detail: str  # a code: CONVERSATION_NOT_FOUND, ACTION_NOT_FOUND:<action_id>, INTERNAL_ERROR
