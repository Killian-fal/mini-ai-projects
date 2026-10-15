from fastapi import APIRouter, status

from interactive_support_api.model import (
    AnswerDto,
    ConversationDto,
    ErrorDto,
    StartConversationDto,
)
from interactive_support_api.service import ConversationService

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={500: {"model": ErrorDto, "description": "INTERNAL_ERROR"}},
)

conversations = ConversationService()

NOT_FOUND = {"model": ErrorDto, "description": "CONVERSATION_NOT_FOUND"}


@router.post("", status_code=status.HTTP_201_CREATED)
def start_conversation(body: StartConversationDto) -> ConversationDto:
    return conversations.start(body)


@router.get("/{conversation_id}", responses={404: NOT_FOUND})
def get_conversation(conversation_id: str) -> ConversationDto:
    return conversations.get(conversation_id)


@router.post(
    "/{conversation_id}/answers",
    responses={
        404: NOT_FOUND,
        409: {"model": ErrorDto, "description": "ACTION_NOT_FOUND:<action_id>"},
    },
)
def answer(conversation_id: str, body: AnswerDto) -> ConversationDto:
    return conversations.answer(conversation_id, body)
