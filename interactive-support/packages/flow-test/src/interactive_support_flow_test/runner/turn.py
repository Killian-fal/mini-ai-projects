from interactive_support_core.engine.flow_helper import find_ask_step
from interactive_support_core.model import (
    Conversation,
    Message,
    MessageCode,
    MessageRole,
    MessageText,
)
from interactive_support_flow_api.model.flow import END, Flow
from interactive_support_flow_api.model.message import TextCode
from interactive_support_flow_api.model.question import (
    ChoiceQuestion,
    ConfirmationQuestion,
    FormQuestion,
    PhotoQuestion,
    TextQuestion,
)
from interactive_support_flow_test.check import check_next_covers
from interactive_support_flow_test.fake import FakeLLM
from interactive_support_flow_test.model import (
    Choice,
    Confirm,
    Form,
    Next,
    Photo,
    Said,
    Text,
)


def said(messages: list[Message], fake: FakeLLM) -> list[Said]:
    """
    The messages of the bot, as the test writes them: the TextCode of a code, the Communication of a generated text.
    """
    codes = {code.key: code for owner in TextCode.__subclasses__() for code in owner}
    result: list[Said] = []
    for message in messages:
        match message:
            case MessageCode(role=MessageRole.ASSISTANT):
                result.append(codes[message.code])
            case MessageText(role=MessageRole.ASSISTANT_GEN):
                result.append(fake.written(message.text))
            case _:
                pass  # the customer's answers, the questions shown, the end of the conversation
    return result


def asked(conversation: Conversation, flow: Flow) -> Next:
    """
    The question pending, its content included. END when the flow has ended.
    """
    pending = conversation.actions.pending()
    if not pending:
        return END
    if len(pending) > 1:
        raise AssertionError(f"MANY_PENDING_ACTIONS:{','.join(pending)}")

    (action_id,) = pending
    step = find_ask_step(flow, action_id)
    ctx = conversation.context
    assert ctx is not None, "a question of the flow is pending: the flow has started"

    match step.question(ctx):
        case ChoiceQuestion() as question:
            question_asked = Choice(step.id, question.options)
        case ConfirmationQuestion() as question:
            question_asked = Confirm(step.id, question.value, question.location)
        case TextQuestion():
            question_asked = Text(step.id)
        case PhotoQuestion():
            question_asked = Photo(step.id)
        case FormQuestion() as question:
            question_asked = Form(
                step.id,
                question.fields,
                {
                    field: value
                    for field in question.fields
                    if (value := question.values.get(field))
                },
            )
        case question:
            raise AssertionError(f"UNKNOWN_QUESTION:{type(question).__name__}")

    check_next_covers(step, question_asked)
    return question_asked
