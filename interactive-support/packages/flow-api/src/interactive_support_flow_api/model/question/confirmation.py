from enum import auto

from pydantic import TypeAdapter, ValidationError

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.question import (
    Question,
    Action,
    ActionYesNo,
    Location,
)
from interactive_support_flow_api.model.message import TextCode


class ConfirmationCode(TextCode):
    NOT_A_BOOLEAN = auto()


class ConfirmationQuestion(Question[bool]):
    value: str
    location: Location | None = None

    def action(self) -> Action:
        return ActionYesNo(value=self.value, location=self.location)

    def parse(self, response: str) -> bool:
        try:
            return TypeAdapter(bool).validate_python(response)
        except ValidationError:
            raise InvalidAnswer(ConfirmationCode.NOT_A_BOOLEAN)
