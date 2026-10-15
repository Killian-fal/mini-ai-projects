import json
from collections.abc import Callable, Mapping, Sequence
from typing import cast

from interactive_support_core.engine import start_flow
from interactive_support_core.handler import handle
from interactive_support_core.model import Conversation, MessageActionResponse
from interactive_support_core.registry import FLOWS
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.model.flow import END, Flow
from interactive_support_flow_api.model.message import TextCode
from interactive_support_flow_api.model.question import ActionGroup
from interactive_support_flow_test import coverage
from interactive_support_flow_test.fake import fake_llm
from interactive_support_flow_test.model import (
    Choice,
    Confirm,
    Form,
    Next,
    Photo,
    Said,
    Text,
)
from interactive_support_flow_test.reply import Reply
from interactive_support_flow_test.runner import turn
from interactive_support_flow_test.runner.display import show


class FlowTest[N: Next]:
    """
    One conversation of `flow` through the real engine, started as if the opening had just ended, played the way the front does.
    Each answer (`choose`, `confirm`, `write`) plays one turn and checks it whole: `said` and `next` are required.
    `llm` scripts every LLM call of the turn, in order: an unscripted or unused reply fails the test.
    """

    def __init__(
        self,
        flow: Flow,
        *,
        order_number: str,
        language: Language,
        llm: Sequence[Reply] = (),
        said: Sequence[Said],
        next: N,
    ):
        if FLOWS.get(flow.issue) is not flow:
            raise AssertionError(
                f"FLOW_NOT_REGISTERED:{flow.issue.value}"
            )  # not in the pyproject's entry points, or `uv sync` not run
        coverage.tested(flow)

        self._flow = flow
        self._conversation = Conversation(
            session_id="flow-test",
            language=language,
            issue=flow.issue,
            order_number=order_number,
            messages=[],
            actions=ActionGroup(children={}),
        )
        self._asked = self._play(start_flow, llm, said, next)

    def choose[E: TextCode, M: Next](
        self: "FlowTest[Choice[E]]",
        option: E,
        *,
        llm: Sequence[Reply] = (),
        said: Sequence[Said],
        next: M,
    ) -> "FlowTest[M]":
        """
        Picks `option` among the proposed ones.
        """
        if not isinstance(self._asked, Choice) or option not in self._asked.options:
            raise _mismatch(option, self._asked)
        return self._answer(option.key, llm, said, next)

    def confirm[M: Next](
        self: "FlowTest[Confirm]",
        value: bool,
        *,
        llm: Sequence[Reply] = (),
        said: Sequence[Said],
        next: M,
    ) -> "FlowTest[M]":
        """
        Accepts (True) or refuses (False) the value to confirm.
        """
        if not isinstance(self._asked, Confirm):
            raise _mismatch(value, self._asked)
        return self._answer("true" if value else "false", llm, said, next)

    def write[M: Next](
        self: "FlowTest[Text]",
        text: str,
        *,
        llm: Sequence[Reply] = (),
        said: Sequence[Said],
        next: M,
    ) -> "FlowTest[M]":
        """
        Answers the free text question with `text`.
        """
        if not isinstance(self._asked, Text):
            raise _mismatch(text, self._asked)
        return self._answer(text, llm, said, next)

    def send_photo[M: Next](
        self: "FlowTest[Photo]",
        photo: str,
        *,
        llm: Sequence[Reply] = (),
        said: Sequence[Said],
        next: M,
    ) -> "FlowTest[M]":
        """
        Answers the photo question with `photo`, the base64 data URI the front sends.
        """
        if not isinstance(self._asked, Photo):
            raise _mismatch(photo, self._asked)
        return self._answer(photo, llm, said, next)

    def fill[E: TextCode, M: Next](
        self: "FlowTest[Form[E]]",
        values: Mapping[E, str],
        *,
        llm: Sequence[Reply] = (),
        said: Sequence[Said],
        next: M,
    ) -> "FlowTest[M]":
        """
        Sends the form with `values`: every field, the pre-filled ones the customer kept included, like the front.
        """
        if not isinstance(self._asked, Form) or set(values) != set(self._asked.fields):
            raise _mismatch(dict(values), self._asked)
        return self._answer(
            json.dumps(
                {field.key: value for field, value in values.items()},
                ensure_ascii=False,
            ),
            llm,
            said,
            next,
        )

    def _answer[M: Next](
        self, response: str, llm: Sequence[Reply], said: Sequence[Said], next: M
    ) -> "FlowTest[M]":
        action_id, _ = (
            self._conversation.ask_next_action()
        )  # the front shows the question
        self._asked = self._play(
            lambda conversation: handle(
                MessageActionResponse(action_id=action_id, response=response),
                conversation,
            ),
            llm,
            said,
            next,
        )
        return cast("FlowTest[M]", self)

    def _play(
        self,
        act: Callable[[Conversation], None],
        llm: Sequence[Reply],
        said: Sequence[Said],
        next: Next,
    ) -> Next:
        before = len(self._conversation.messages)
        with fake_llm(*llm) as fake, coverage.recording():
            act(self._conversation)

        # the engine keeps nothing beside the Conversation: the next turn starts from its JSON
        restored = Conversation.model_validate_json(
            self._conversation.model_dump_json()
        )
        if restored != self._conversation:
            raise AssertionError(
                f"CONVERSATION_NOT_SERIALIZABLE:\n  before: {self._conversation!r}\n  after:  {restored!r}"
            )
        self._conversation = restored

        actual_said = turn.said(self._conversation.messages[before:], fake)
        actual_next = turn.asked(self._conversation, self._flow)
        # StepIds are StrEnums: the X steps of two flows are ==, so the step is compared by identity
        if (
            list(said) != actual_said
            or next != actual_next
            or getattr(next, "step", None) is not getattr(actual_next, "step", None)
        ):
            raise AssertionError(
                "TURN_MISMATCH:\n"
                f"  said expected: {show(list(said))}\n  said actual:   {show(actual_said)}\n"
                f"  next expected: {show(next)}\n  next actual:   {show(actual_next)}"
            )
        return actual_next


def _mismatch(answer: object, asked: Next) -> AssertionError:
    if asked is END:
        return AssertionError(f"ANSWER_AFTER_END:{show(answer)}")
    return AssertionError(f"ANSWER_MISMATCH:{show(answer)}:{show(asked)}")
