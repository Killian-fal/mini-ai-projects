from enum import auto

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.question import (
    Question,
    Action,
    ActionUniqueChoice,
)
from interactive_support_flow_api.model.message import TextCode


class ChoiceCode(TextCode):
    UNKNOWN_CHOICE = auto()


class ChoiceQuestion[E: TextCode](Question[E]):
    """
    The options are TextCodes: the front shows their translation and sends back their key.
    """

    options: list[E]

    def action(self) -> Action:
        return ActionUniqueChoice(choices=[option.key for option in self.options])

    def parse(self, response: str) -> E:
        for option in self.options:
            if option.key == response:
                return option
        raise InvalidAnswer(ChoiceCode.UNKNOWN_CHOICE)
