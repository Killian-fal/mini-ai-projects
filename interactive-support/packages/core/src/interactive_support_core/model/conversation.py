from pydantic import BaseModel

from interactive_support_core.model import Message, MessageAction
from interactive_support_flow_api.model.context import FlowContext, Issue, Language
from interactive_support_flow_api.model.question import Action, ActionGroup


class Conversation(BaseModel):
    session_id: str
    language: Language
    issue: Issue | None
    order_number: str | None

    messages: list[
        Message
    ]  # only for tracability, never use this to make any logic decision
    actions: ActionGroup
    context: FlowContext | None = (
        None  # set by the flow engine once the opening is done
    )

    def ask_next_action(self) -> tuple[str, Action]:
        action_id, action = next(iter(self.actions.pending().items()))
        self.messages.append(MessageAction(action_id=action_id, action=action))
        return action_id, action

    def complete_action(self, action_id: str):
        self.actions.remove(action_id)

    def ask_more_actions(self, action_id: str, actions: dict[str, Action]):
        self.actions.replace(action_id, actions)
