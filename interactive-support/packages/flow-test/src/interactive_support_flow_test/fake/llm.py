# pyright: reportPrivateUsage=false
# flow-test replaces the private parts of flow-api that call the LLM, and reads the questions of a classify
from collections import deque
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from importlib import import_module
from typing import Any

import pytest

from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.tools.communication import Communication
from interactive_support_flow_api.tools.llm import GenerateInput, GenerateOutput
from interactive_support_flow_api.tools.llm.classify import Classify, _Question
from interactive_support_flow_test.reply import ClassifyReply, GenerateReply, Reply


class FakeLLM:
    """
    Replaces every LLM call inside `fake_llm`: a test never calls a real LLM.
    """

    def __init__(self, replies: Sequence[Reply]):
        self._replies: deque[Reply] = deque(replies)
        self._written: dict[str, Communication] = {}

    def check_all_used(self):
        if self._replies:
            unused, self._replies = list(self._replies), deque()
            raise AssertionError(f"UNUSED_LLM_REPLY:{unused}")

    def written(self, text: str) -> Communication:
        """
        The Communication a generated text stands for.
        """
        return self._written[text]

    def classify(
        self, inputs: dict[str, str], questions: list[_Question]
    ) -> tuple[Any, ...]:
        call = (
            f"classify({inputs}, questions={[question.text for question in questions]})"
        )
        reply = self._pop(call)
        if (
            not isinstance(reply, ClassifyReply)
            or dict(reply.given) != inputs
            or len(reply.answers) != len(questions)
            or any(
                answer.question != question.text
                for answer, question in zip(reply.answers, questions)
            )
        ):
            raise AssertionError(
                f"LLM_CALL_MISMATCH:\n  scripted: {reply}\n  called:   {call}"
            )
        return tuple(answer.result for answer in reply.answers)

    def generate[O: GenerateOutput](
        self, instruction: str, generate_input: GenerateInput, generate_output: type[O]
    ) -> O:
        call = f"generate({generate_input!r}) -> {generate_output.__name__}"
        reply = self._pop(call)
        if (
            not isinstance(reply, GenerateReply)
            or reply.given != generate_input
            or not isinstance(reply.output, generate_output)
        ):
            raise AssertionError(
                f"LLM_CALL_MISMATCH:\n  scripted: {reply}\n  called:   {call}"
            )
        return reply.output

    def write(self, language: Language, communication: Communication) -> str:
        """
        Nothing to script: the text is a unique token, read back as `communication` in the turn's `said`.
        """
        text = f"<generated {len(self._written)}>"
        self._written[text] = communication
        return text

    def _pop(self, call: str) -> Reply:
        if not self._replies:
            raise AssertionError(f"UNSCRIPTED_LLM_CALL:{call}")
        return self._replies.popleft()


@contextmanager
def fake_llm(*replies: Reply) -> Generator[FakeLLM]:
    """
    Every LLM call inside gets the next reply, in order: an unscripted call or a reply left unused fails.
    """
    fake = FakeLLM(replies)

    def run(classify: Classify[*tuple[Any, ...]]) -> tuple[Any, ...]:
        return fake.classify(classify._inputs, classify._questions)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Classify, "run", run)
        # import_module: `llm.generate` and `communication.generate` are the functions their package exports, not the modules
        patch.setattr(
            import_module("interactive_support_flow_api.tools.llm.generate"),
            "_call",
            fake.generate,
        )
        patch.setattr(
            import_module("interactive_support_flow_api.tools.communication.generate"),
            "_write",
            fake.write,
        )
        yield fake
    fake.check_all_used()
