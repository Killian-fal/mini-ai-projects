import pytest
from pydantic import Field

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.tools import llm


class CustomerMessage(llm.GenerateInput):
    text: str = Field(description="The customer's message")


class Summary(llm.GenerateOutput):
    text: str = Field(description="The message in a few words")


# raised before the LLM call: otherwise the fake LLM would fail with UNSCRIPTED_LLM_CALL
def test_llm_field_conflict():
    with pytest.raises(InternalError, match="^LLM_FIELD_CONFLICT$"):
        llm.generate(
            "Summarize the message.",
            CustomerMessage(text="Où est mon colis ?"),
            Summary,
        )
