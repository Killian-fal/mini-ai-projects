from importlib.metadata import entry_points

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.flow import Flow
from interactive_support_flow_api.model.context import Issue
from interactive_support_core.opening.code import IssueChoice

# each flow package declares its Flow in its pyproject.toml, under [project.entry-points."interactive_support.flows"]
_FLOW_LIST: list[Flow] = [
    entry_point.load()
    for entry_point in sorted(
        entry_points(group="interactive_support.flows"),
        key=lambda entry_point: entry_point.name,
    )
]
FLOWS: dict[Issue, Flow] = {flow.issue: flow for flow in _FLOW_LIST}


def check_flows():
    issues = [flow.issue for flow in _FLOW_LIST]
    if duplicated := sorted(
        {issue.value for issue in issues if issues.count(issue) > 1}
    ):
        raise InternalError(f"FLOW_DUPLICATED:{','.join(duplicated)}")
    if missing := sorted(issue.value for issue in Issue if issue not in FLOWS):
        raise InternalError(f"FLOW_MISSING:{','.join(missing)}")
    if missing := sorted(
        issue.value
        for issue in Issue
        if issue not in {choice.value for choice in IssueChoice}
    ):
        raise InternalError(
            f"ISSUE_CHOICE_MISSING:{','.join(missing)}"
        )  # the opening can't offer it to the customer
