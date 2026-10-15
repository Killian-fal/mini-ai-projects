from uuid import uuid4

from interactive_support_api.exception import ActionNotFound, ConversationNotFound
from interactive_support_api.mapper import ConversationMapper, MessageMapper
from interactive_support_api.model import (
    AnswerDto,
    ConversationDto,
    StartConversationDto,
)
from interactive_support_core.handler import handle
from interactive_support_core.model import Conversation
from interactive_support_core.opening.handler import open_conversation
from interactive_support_observability import trace_session


class ConversationService:
    def __init__(self):
        self._conversations: dict[str, str] = {}

    def start(self, opening: StartConversationDto) -> ConversationDto:
        session_id = str(uuid4())
        with trace_session(session_id):
            conversation = open_conversation(opening.message, session_id)
        return self._save(conversation)

    def get(self, conversation_id: str) -> ConversationDto:
        return ConversationMapper.to_dto(self._load(conversation_id))

    def answer(self, conversation_id: str, answer: AnswerDto) -> ConversationDto:
        conversation = self._load(conversation_id)

        # TODO: temp rework duplication
        if answer.action_id not in conversation.actions.pending():
            raise ActionNotFound(f"ACTION_NOT_FOUND:{answer.action_id}")

        with trace_session(conversation_id):
            handle(MessageMapper.from_answer(answer), conversation)
        return self._save(conversation)

    def _load(self, conversation_id: str) -> Conversation:
        if conversation_id not in self._conversations:
            raise ConversationNotFound("CONVERSATION_NOT_FOUND")
        return Conversation.model_validate_json(self._conversations[conversation_id])

    def _save(self, conversation: Conversation) -> ConversationDto:
        if conversation.actions.pending():
            conversation.ask_next_action()

        shown = ConversationMapper.to_dto(conversation)
        self._conversations[conversation.session_id] = conversation.model_dump_json()
        return shown
