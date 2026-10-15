from interactive_support_api.mapper.message import MessageMapper
from interactive_support_api.model import ConversationDto
from interactive_support_core.model import Conversation


class ConversationMapper:
    @staticmethod
    def to_dto(conversation: Conversation) -> ConversationDto:
        return ConversationDto(
            id=conversation.session_id,
            language=conversation.language,
            messages=[
                MessageMapper.to_dto(message, conversation.language)
                for message in conversation.messages
            ],
        )
