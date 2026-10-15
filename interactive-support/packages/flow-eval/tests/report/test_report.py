from interactive_support_flow_eval.report import Outcome, Report


def test_report_counts_the_criteria_and_the_groups_apart_and_the_errors_as_failed():
    report = Report(
        name="routing",
        criteria=("language", "issues"),
        outcomes=(
            Outcome(
                input='"annuler"',
                expected='["CANCEL"]',
                group="cancel",
                output='["FR",["CANCEL"]]',
                failed_criteria=(),
                error=None,
            ),
            Outcome(
                input='"cassé"',
                expected='["DAMAGED"]',
                group="damaged",
                output='["FR",[]]',
                failed_criteria=("issues",),
                error=None,
            ),
            Outcome(
                input='"bonjour"',
                expected="[]",
                group="out_of_scope",
                output="",
                failed_criteria=(),
                error="InternalError: LLM_MISSING_PROBABILITY",
            ),
        ),
        url="http://mlflow/run",
    )

    assert report.lines() == [
        "routing",
        "  1/3 pass every criterion: 33% (95% CI 6%-79%)",
        "  language  2/3",
        "  issues    1/3",
        "  group cancel        1/1",
        "  group damaged       0/1",
        "  group out_of_scope  0/1",
        '  failed issues: "cassé" expected ["DAMAGED"], got ["FR",[]]',
        '  raised: "bonjour" InternalError: LLM_MISSING_PROBABILITY',
        "  http://mlflow/run",
    ]
