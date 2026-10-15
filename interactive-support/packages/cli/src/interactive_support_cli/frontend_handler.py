import base64
import json
import mimetypes
from pathlib import Path

from interactive_support_cli.display import t
from interactive_support_core.model import Conversation, MessageActionResponse
from interactive_support_flow_api.model.question import (
    Action,
    ActionForm,
    ActionPhotoUpload,
    ActionUniqueChoice,
)


def frontend_handler(
    action_id: str, action: Action, conversation: Conversation
) -> MessageActionResponse:
    if isinstance(action, ActionForm):
        form = {
            key: input(f"  {t(conversation.language, key)} [{value}] > ") or value
            for key, value in action.fields.items()
        }
        return MessageActionResponse(
            action_id=action_id, response=json.dumps(form, ensure_ascii=False)
        )

    user_text = input("> ")

    if (
        isinstance(action, ActionUniqueChoice)
        and user_text.isdigit()
        and 1 <= int(user_text) <= len(action.choices)
    ):
        user_text = action.choices[
            int(user_text) - 1
        ]  # like a button: the front shows the label, sends back the key

    if isinstance(action, ActionPhotoUpload) and Path(user_text).is_file():
        # like the front: the photo is sent as a base64 data URI
        mime, _ = mimetypes.guess_type(user_text)
        content = base64.b64encode(Path(user_text).read_bytes()).decode()
        user_text = f"data:{mime};base64,{content}"

    return MessageActionResponse(action_id=action_id, response=user_text)
