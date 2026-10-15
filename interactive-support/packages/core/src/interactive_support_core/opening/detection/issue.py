from enum import Enum

from interactive_support_core.opening.code import IssueChoice
from interactive_support_core.registry import FLOWS
from interactive_support_flow_api.model.context import Issue
from interactive_support_flow_api.tools import llm

ISSUE_QUESTION = "Which issue does the customer have?"

IssueDetection = Enum(
    "IssueDetection",
    {issue.name: flow.description for issue, flow in FLOWS.items()}
    | {"OTHER": "Other issues, not in the choices"},
)


def to_issue_candidates(result: llm.ChoiceResult[Enum]) -> list[IssueChoice]:
    if result.value.name == "OTHER":
        return []

    if result.confidence >= 0.7:
        return [IssueChoice(Issue[result.value.name])]

    sorted_prob = sorted(
        result.probabilities.items(), key=lambda item: item[1], reverse=True
    )
    return [
        IssueChoice(Issue[detected.name])
        for detected, probability in sorted_prob
        if probability > 0 and detected.name != "OTHER"
    ]
