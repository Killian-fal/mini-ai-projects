from collections import Counter

from pydantic import BaseModel

from interactive_support_flow_eval.report.outcome import Outcome
from interactive_support_flow_eval.report.wilson import wilson


class Report(BaseModel):
    name: str
    criteria: tuple[str, ...]
    outcomes: tuple[Outcome, ...]
    url: str

    def passed_criterion(self, criterion: str) -> int:
        return sum(
            outcome.error is None and criterion not in outcome.failed_criteria
            for outcome in self.outcomes
        )

    def passed_every_criterion(self) -> int:
        return sum(
            outcome.error is None and not outcome.failed_criteria
            for outcome in self.outcomes
        )

    def groups(self) -> dict[str, int]:
        return dict(sorted(Counter(outcome.group for outcome in self.outcomes).items()))

    def passed_group(self, group: str) -> int:
        return sum(
            outcome.error is None and not outcome.failed_criteria
            for outcome in self.outcomes
            if outcome.group == group
        )

    def lines(self) -> list[str]:
        total = len(self.outcomes)
        passed = self.passed_every_criterion()
        low, high = wilson(passed, total)
        width = max(map(len, self.criteria))
        groups = self.groups()
        group_width = max(map(len, groups))
        return [
            self.name,
            f"  {passed}/{total} pass every criterion: {passed / total:.0%} (95% CI {low:.0%}-{high:.0%})",
            *(
                f"  {criterion:<{width}}  {self.passed_criterion(criterion)}/{total}"
                for criterion in self.criteria
            ),
            *(
                f"  group {group:<{group_width}}  {self.passed_group(group)}/{group_total}"
                for group, group_total in groups.items()
            ),
            *(
                f"  failed {', '.join(outcome.failed_criteria)}: {outcome.input} expected {outcome.expected}, got {outcome.output}"
                for outcome in self.outcomes
                if outcome.error is None and outcome.failed_criteria
            ),
            *(
                f"  raised: {outcome.input} {outcome.error}"
                for outcome in self.outcomes
                if outcome.error is not None
            ),
            f"  {self.url}",
        ]
