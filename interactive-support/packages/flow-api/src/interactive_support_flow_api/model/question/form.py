from enum import auto

from pydantic import TypeAdapter, ValidationError

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.question import Question, Action, ActionForm
from interactive_support_flow_api.model.message import TextCode


class FormCode(TextCode):
    NOT_A_FORM = auto()
    MISSING_FIELD = auto()


class FormQuestion[E: TextCode](Question[dict[E, str]]):
    fields: list[E]
    values: dict[E, str | None] = {}

    def action(self) -> Action:
        return ActionForm(
            fields={field.key: self.values.get(field) or "" for field in self.fields}
        )

    def parse(self, response: str) -> dict[E, str]:
        try:
            sent = TypeAdapter(dict[str, str]).validate_json(response)
        except ValidationError:
            raise InvalidAnswer(FormCode.NOT_A_FORM)

        answer = {field: sent.get(field.key, "").strip() for field in self.fields}
        if not all(answer.values()):
            raise InvalidAnswer(FormCode.MISSING_FIELD)
        return answer
