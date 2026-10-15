from interactive_support_api.exception import ApiError
from interactive_support_api.mapper.action import ActionMapper
from interactive_support_api.model import (
    AnswerDto,
    MessageActionDto,
    MessageActionResponseDto,
    MessageCodeDto,
    MessageDto,
    MessageTextDto,
)
from interactive_support_api.translation import t, t_or_none
from interactive_support_core.model import (
    Message,
    MessageAction,
    MessageActionResponse,
    MessageCode,
    MessageRole,
    MessageText,
)
from interactive_support_flow_api.model.context import Language


class MessageMapper:
    @staticmethod
    def to_dto(message: Message, language: Language) -> MessageDto:
        match message:
            case MessageText(role=MessageRole.USER | MessageRole.ASSISTANT_GEN as role):
                return MessageTextDto(role=role, text=message.text)
            case MessageCode(role=MessageRole.ASSISTANT | MessageRole.END as role):
                return MessageCodeDto(
                    role=role,
                    code=message.code,
                    text=t(language, message.code),
                )
            case MessageAction(role=MessageRole.ASSISTANT_ACTION as role):
                return MessageActionDto(
                    role=role,
                    action_id=message.action_id,
                    action=ActionMapper.to_dto(message.action, language),
                )
            case MessageActionResponse(role=MessageRole.USER_ACTION_RESPONSE as role):
                return MessageActionResponseDto(
                    role=role,
                    action_id=message.action_id,
                    response=message.response,
                    label=t_or_none(language, message.response),
                )
            case _:
                raise ApiError(
                    f"MESSAGE_UNKNOWN:{type(message).__name__}:{message.role.value}"
                )

    @staticmethod
    def from_answer(answer: AnswerDto) -> MessageActionResponse:
        return MessageActionResponse(
            action_id=answer.action_id, response=answer.response
        )
