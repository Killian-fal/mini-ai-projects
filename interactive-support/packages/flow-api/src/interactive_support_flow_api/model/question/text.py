from interactive_support_flow_api.model.question import (
    Question,
    Action,
    ActionTextInput,
)


class TextQuestion(Question[str]):
    def action(self) -> Action:
        return ActionTextInput()

    def parse(self, response: str) -> str:
        return response
