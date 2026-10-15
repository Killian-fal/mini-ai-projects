from interactive_support_core.model import (
    Conversation,
    MessageActionResponse,
    MessageCode,
    MessageRole,
    MessageText,
)
from interactive_support_core.opening.code import OpeningCode, IssueChoice
from interactive_support_core.opening.detection import (
    detect_first_message,
    detect_issue,
    extract_order_number,
)
from interactive_support_core.opening.required_message_id import RequiredMessageId
from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.message import TextCode
from interactive_support_flow_api.model.question import (
    ActionGroup,
    ChoiceQuestion,
    TextQuestion,
)


def open_conversation(message: str, session_id: str) -> Conversation:
    language, candidates = detect_first_message(message)
    conversation = Conversation(
        session_id=session_id,
        language=language,
        issue=None,
        order_number=extract_order_number(message),
        messages=[MessageText(role=MessageRole.USER, text=message)],
        actions=ActionGroup(children={}),
    )
    _ask_issue(conversation, candidates)
    return conversation


def opening_handler(response: MessageActionResponse, conversation: Conversation):
    """
    One question at a time: the issue, always confirmed by the customer, then the order number if the first message had none.
    Raises InvalidAnswer before changing anything: the same question is asked again.
    """
    match response.action_id:
        case RequiredMessageId.ISSUE:
            candidates = detect_issue(response.response)
            conversation.complete_action(response.action_id)
            if conversation.order_number is None:
                conversation.order_number = extract_order_number(response.response)
            _ask_issue(conversation, candidates)

        case RequiredMessageId.ISSUE_CHOICE:
            choice = ChoiceQuestion(options=list(IssueChoice)).parse(response.response)
            conversation.complete_action(response.action_id)
            if choice.value is None:
                _ask_issue(
                    conversation, []
                )  # "something else": the customer describes it
                return

            conversation.issue = choice.value
            _add_assistant_message(conversation, OpeningCode.VALID_ISSUE)
            if conversation.order_number is None:
                _add_assistant_message(conversation, OpeningCode.ASK_ORDER_NUMBER)
                conversation.actions.add(
                    RequiredMessageId.ORDER_NUMBER, TextQuestion().action()
                )

        case RequiredMessageId.ORDER_NUMBER:
            order_number = extract_order_number(response.response)
            if order_number is None:
                raise InvalidAnswer(OpeningCode.ORDER_NUMBER_UNREADABLE)

            conversation.order_number = order_number
            conversation.complete_action(response.action_id)
            _add_assistant_message(conversation, OpeningCode.VALID_ORDER_NUMBER)

        case _:
            raise InternalError(f"ACTION_NOT_FOUND:{response.action_id}")


def _ask_issue(conversation: Conversation, candidates: list[IssueChoice]):
    if candidates:
        _add_assistant_message(conversation, OpeningCode.ASK_ISSUE_CHOICE)
        conversation.actions.add(
            RequiredMessageId.ISSUE_CHOICE,
            ChoiceQuestion(options=[*candidates, IssueChoice.OTHER]).action(),
        )
    else:
        _add_assistant_message(conversation, OpeningCode.ASK_ISSUE)
        conversation.actions.add(RequiredMessageId.ISSUE, TextQuestion().action())


def _add_assistant_message(conversation: Conversation, code: TextCode):
    conversation.messages.append(MessageCode(role=MessageRole.ASSISTANT, code=code.key))
