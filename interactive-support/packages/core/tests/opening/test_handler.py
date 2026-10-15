"""
The opening, with the LLM scripted by flow-test: `play` runs a whole conversation, the test checks its transcript.
Once the issue and the order number are known, CANCEL takes over: its first message ends what the opening checks.
"""

from collections.abc import Sequence

import pytest

from interactive_support_core.handler import handle
from interactive_support_core.model import (
    Conversation,
    MessageAction,
    MessageActionResponse,
    MessageCode,
    MessageRole,
    MessageText,
)
from interactive_support_core.opening.code import IssueChoice, OpeningCode
from interactive_support_core.opening.detection.issue import (
    ISSUE_QUESTION,
    IssueDetection,
)
from interactive_support_core.opening.detection.language import (
    LANGUAGE_QUESTION,
    LanguageDetection,
)
from interactive_support_core.opening.handler import open_conversation
from interactive_support_core.opening.required_message_id import RequiredMessageId
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.model.message import TextCode
from interactive_support_flow_api.model.question import (
    Action,
    ActionTextInput,
    ActionUniqueChoice,
)
from interactive_support_flow_cancel.code import CancelCode
from interactive_support_flow_test import fake_llm, reply
from interactive_support_flow_test.reply import Answer, Reply

CANCEL = IssueDetection["CANCEL"]
DAMAGED = IssueDetection["DAMAGED"]
OTHER = IssueDetection["OTHER"]

FRENCH = reply.choose(LANGUAGE_QUESTION, LanguageDetection.FR)
SURELY_CANCEL = reply.choose(ISSUE_QUESTION, CANCEL)

ISSUE_ASKED: dict[str, Action] = {RequiredMessageId.ISSUE: ActionTextInput()}
ISSUE_CHOICE_ASKED: dict[str, Action] = {
    RequiredMessageId.ISSUE_CHOICE: ActionUniqueChoice(
        choices=[IssueChoice.CANCEL.key, IssueChoice.OTHER.key]
    )
}


def play(first_message: str, *answers: str, llm: Sequence[Reply]) -> Conversation:
    """
    The customer's first message, then their answers to each pending action, as the front sends them.
    `llm` scripts every LLM call of the conversation, in order.
    """
    with fake_llm(*llm):
        conversation = _from_json(open_conversation(first_message, session_id="test"))
        for response in answers:
            action_id, _ = conversation.ask_next_action()
            handle(
                MessageActionResponse(action_id=action_id, response=response),
                conversation,
            )
            conversation = _from_json(conversation)
    return conversation


def _from_json(conversation: Conversation) -> Conversation:
    # the engine keeps nothing beside the Conversation: each turn starts from its JSON
    restored = Conversation.model_validate_json(conversation.model_dump_json())
    assert restored == conversation, "CONVERSATION_NOT_SERIALIZABLE"
    return restored


def transcript(conversation: Conversation) -> list[str | TextCode]:
    """
    What the customer sent (str) and what the bot said (TextCode), in order.
    """
    codes = {code.key: code for owner in TextCode.__subclasses__() for code in owner}
    result: list[str | TextCode] = []
    for message in conversation.messages:
        match message:
            case MessageText(role=MessageRole.USER):
                result.append(message.text)
            case MessageActionResponse():
                result.append(message.response)
            case MessageCode():
                result.append(codes[message.code])
            case MessageAction():
                pass  # the action shown: the code just before says what it asks
            case _:
                raise AssertionError(f"UNEXPECTED_MESSAGE:{message!r}")
    return result


def detection(message: str, language: Answer, issue: Answer) -> Reply:
    """
    The first message: its language and its issue, in a single call.
    """
    return reply.classify({"customer_message": message}, language, issue)


@pytest.mark.parametrize(
    "issue, said, asked",
    [
        pytest.param(
            SURELY_CANCEL, OpeningCode.ASK_ISSUE_CHOICE, ISSUE_CHOICE_ASKED, id="sure"
        ),
        pytest.param(
            reply.choose(
                ISSUE_QUESTION,
                CANCEL,
                confidence=0.4,
                probabilities={CANCEL: 0.6, DAMAGED: 0.0, OTHER: 0.4},
            ),
            OpeningCode.ASK_ISSUE_CHOICE,
            ISSUE_CHOICE_ASKED,
            id="unsure",
        ),
        pytest.param(
            reply.choose(
                ISSUE_QUESTION,
                OTHER,
                confidence=0.3,
                probabilities={CANCEL: 0.45, DAMAGED: 0.0, OTHER: 0.55},
            ),
            OpeningCode.ASK_ISSUE,
            ISSUE_ASKED,
            id="other, even close to cancel",
        ),
    ],
)
def test_issue_detection(issue: Answer, said: OpeningCode, asked: dict[str, Action]):
    message = "Je voudrais annuler ma commande cma_001"
    conversation = play(message, llm=[detection(message, FRENCH, issue)])

    assert transcript(conversation) == [message, said]
    assert conversation.actions.pending() == asked


@pytest.mark.parametrize(
    "language, expected",
    [
        pytest.param(FRENCH, Language.FR, id="sure"),
        pytest.param(
            reply.choose(
                LANGUAGE_QUESTION,
                LanguageDetection.FR,
                confidence=0.4,
                probabilities={
                    LanguageDetection.FR: 0.6,
                    LanguageDetection.EN: 0.3,
                    LanguageDetection.OTHER: 0.1,
                },
            ),
            Language.EN,
            id="unsure",
        ),
        pytest.param(
            reply.choose(LANGUAGE_QUESTION, LanguageDetection.OTHER),
            Language.EN,
            id="other",
        ),
    ],
)
def test_language_falls_back_to_english(language: Answer, expected: Language):
    message = "Je voudrais annuler ma commande cma_001"
    conversation = play(message, llm=[detection(message, language, SURELY_CANCEL)])

    assert conversation.language is expected


def test_something_else_is_described_again():
    message, description = (
        "Bonjour, c'est pour la commande cma_001",
        "Je n'en veux plus",
    )
    conversation = play(
        message,
        IssueChoice.OTHER.key,
        description,
        IssueChoice.CANCEL.key,
        llm=[
            detection(message, FRENCH, SURELY_CANCEL),
            # only the issue is detected again: the language stays the one of the first message
            reply.classify({"customer_message": description}, SURELY_CANCEL),
        ],
    )

    assert transcript(conversation) == [
        message,
        OpeningCode.ASK_ISSUE_CHOICE,
        IssueChoice.OTHER.key,
        OpeningCode.ASK_ISSUE,
        description,
        OpeningCode.ASK_ISSUE_CHOICE,
        IssueChoice.CANCEL.key,
        OpeningCode.VALID_ISSUE,
        CancelCode.ASK_PROPOSAL,
    ]


def test_order_number_given_with_the_issue_is_not_asked_again():
    message, description = "Bonjour", "Je veux annuler la commande cma_001"
    conversation = play(
        message,
        description,
        IssueChoice.CANCEL.key,
        llm=[
            detection(message, FRENCH, reply.choose(ISSUE_QUESTION, OTHER)),
            reply.classify({"customer_message": description}, SURELY_CANCEL),
        ],
    )

    assert transcript(conversation) == [
        message,
        OpeningCode.ASK_ISSUE,
        description,
        OpeningCode.ASK_ISSUE_CHOICE,
        IssueChoice.CANCEL.key,
        OpeningCode.VALID_ISSUE,
        CancelCode.ASK_PROPOSAL,
    ]


def test_order_number_is_asked_until_readable():
    message = "Je voudrais annuler ma commande"
    conversation = play(
        message,
        IssueChoice.CANCEL.key,
        "Je ne l'ai plus",
        "C'est la CMA_001",
        llm=[detection(message, FRENCH, SURELY_CANCEL)],
    )

    assert transcript(conversation) == [
        message,
        OpeningCode.ASK_ISSUE_CHOICE,
        IssueChoice.CANCEL.key,
        OpeningCode.VALID_ISSUE,
        OpeningCode.ASK_ORDER_NUMBER,
        "Je ne l'ai plus",
        OpeningCode.ORDER_NUMBER_UNREADABLE,
        "C'est la CMA_001",
        OpeningCode.VALID_ORDER_NUMBER,
        CancelCode.ASK_PROPOSAL,
    ]


def test_first_message_to_the_end():
    # the order number of the first message isn't asked again
    # #CMA_003 is shipped: CANCEL refuses and ends, the order doesn't change
    message = "Bonjour, je veux annuler ma commande cma_003"
    conversation = play(
        message,
        IssueChoice.CANCEL.key,
        llm=[detection(message, FRENCH, SURELY_CANCEL)],
    )

    assert transcript(conversation) == [
        message,
        OpeningCode.ASK_ISSUE_CHOICE,
        IssueChoice.CANCEL.key,
        OpeningCode.VALID_ISSUE,
        CancelCode.TOO_LATE_TO_CANCEL,
        OpeningCode.COMPLETE_CONVERSATION,
    ]
