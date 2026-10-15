import os
from collections.abc import Callable, Mapping, Sequence

import dspy
from pydantic_core import to_json

from interactive_support_flow_eval.model import Case
from interactive_support_flow_eval.report import Outcome, Report
from interactive_support_flow_eval.runner.program import Program, passed

_EXPERIMENT = "interactive-support-evals"


def evaluate[Input, Expected, Output](
    name: str,
    cases: Sequence[Case[Input, Expected]],
    *,
    run: Callable[[Input], Output],
    criteria: Mapping[str, Callable[[Output, Expected], bool]],
) -> None:
    """
    name: the run in MLflow, and the title of the report printed (`make eval` shows it).
    run: the real function evaluated, called with the input of each case.
    criteria: each checks the output against what the case expects. Named, they are reported apart.
    """
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if not cases:
        raise AssertionError("EVAL_WITHOUT_CASES")
    if not criteria:
        raise AssertionError("EVAL_WITHOUT_CRITERIA")
    if not tracking_uri:
        raise AssertionError("EVAL_WITHOUT_MLFLOW")

    import mlflow
    import mlflow.dspy as mlflow_dspy

    dspy.configure_cache(enable_disk_cache=False, enable_memory_cache=False)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(_EXPERIMENT)
    mlflow_dspy.autolog(log_evals=True)

    devset = [
        dspy.Example(
            index=index,
            input=to_json(case.input, serialize_unknown=True).decode(),
            expected=to_json(case.expected, serialize_unknown=True).decode(),
            group=case.group,
        ).with_inputs("index")
        for index, case in enumerate(cases)
    ]
    with mlflow.start_run(run_name=name) as tracked:
        result = dspy.Evaluate(devset=devset, metric=passed, num_threads=8)(
            Program(cases, run, criteria)
        )
        outcomes = tuple(
            Outcome(
                input=example.input,
                expected=example.expected,
                group=example.group,
                output=prediction.output,
                failed_criteria=tuple(prediction.failed_criteria),
                error=prediction.error,
            )
            for example, prediction, _ in result.results
        )
        report = Report(
            name=name,
            criteria=tuple(criteria),
            outcomes=outcomes,
            url=f"{tracking_uri}/#/experiments/{tracked.info.experiment_id}/runs/{tracked.info.run_id}",
        )
        mlflow.log_metrics(
            {
                f"criterion.{criterion}": report.passed_criterion(criterion)
                / len(outcomes)
                for criterion in criteria
            }
            | {
                f"group.{group}": report.passed_group(group) / total
                for group, total in report.groups().items()
            }
        )
    print("\n".join(report.lines()))

    if raised := [outcome for outcome in outcomes if outcome.error is not None]:
        raise AssertionError(f"EVAL_CASE_RAISED:{len(raised)}:{raised[0].error}")
