from interactive_support_core.model import (
    Conversation,
    Message,
    MessageText,
    MessageCode,
    MessageAction,
    MessageActionResponse,
)
from interactive_support_core.translation import translations
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.model.question import (
    Action,
    ActionUniqueChoice,
    ActionYesNo,
)


def t(language: Language, key: str) -> str:
    """
    The CLI plays the front: like i18next's t(), the key itself when it has no translation.
    """
    owner, _, name = key.partition(".")
    return translations(language).get(owner, {}).get(name, key)


def format_action(action: Action, language: Language) -> str:
    match action:
        case ActionUniqueChoice():
            return "".join(
                f"\n      {i}. {t(language, choice)}"
                for i, choice in enumerate(action.choices, 1)
            )
        case ActionYesNo():
            return f" : {action.value} [y/n]"
        case _:
            return f" ({action.type.value})"


def format_message(message: Message, language: Language) -> str:
    match message:
        case MessageText():
            return f"[{message.role.value}] {message.text}"
        case MessageCode():
            return f"[{message.role.value}] {t(language, message.code)}"
        case MessageAction():
            return f"[{message.role.value}] {message.action_id}{format_action(message.action, language)}"
        case MessageActionResponse():
            response = t(language, message.response)
            if len(response) > 80:  # a photo is a whole base64 data URI
                response = response[:77] + "..."
            return f"[{message.role.value}] {message.action_id} -> {response}"
        case _:
            return f"[{message.role.value}] {repr(message)}"


def print_messages(conversation: Conversation, start: int = 0) -> int:
    for i, message in enumerate(conversation.messages[start:], start + 1):
        print(f"{i:>2}. {format_message(message, conversation.language)}")
    return len(conversation.messages)


def print_conversation(conversation: Conversation):
    print("=" * 60)
    print(f"Session  : {conversation.session_id}")
    print(f"Langue   : {conversation.language.value}")
    print(f"Problème : {conversation.issue.value if conversation.issue else '-'}")
    print(f"Commande : {conversation.order_number or '-'}")
    print("-" * 60)

    print_messages(conversation)

    if conversation.actions.pending():
        print("-" * 60)
        print("Actions en attente : " + ", ".join(conversation.actions.pending()))

    print("=" * 60)
