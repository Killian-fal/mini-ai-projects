from typing import Any

from pydantic import BaseModel

from interactive_support_flow_api.model.flow import Step, AskStep, StepId
from interactive_support_flow_api.model.context import Issue


class Flow(BaseModel):
    issue: Issue
    description: (
        str  # for the LLM that finds the issue in the opening, never shown to the user
    )
    steps: list[Step | AskStep[Any]]

    def action_id(self, step_id: StepId) -> str:
        return f"{self.issue.value}.{step_id.name}"
