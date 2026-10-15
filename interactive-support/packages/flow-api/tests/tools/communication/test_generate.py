import pytest
from pydantic import Field

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.context import FlowContext, Issue, Language
from interactive_support_flow_api.tools import communication
from interactive_support_flow_api.tools.communication import Communication


class Apology(Communication):
    __instruction__ = "Apologize for the delay."

    text: str = Field(description="The customer's complaint")


# raised before the LLM call: otherwise the fake LLM would fail with UNSCRIPTED_LLM_CALL
def test_llm_field_conflict():
    ctx = FlowContext(issue=Issue.CANCEL, order_number="#CMA_001", language=Language.FR)

    with pytest.raises(InternalError, match="^LLM_FIELD_CONFLICT$"):
        communication.generate(ctx, Apology(text="Toujours rien reçu"))
