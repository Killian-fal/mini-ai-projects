"""
The LLM call of report.py, on the photos customers send of their damaged order: `report/`, one file per kind of case,
the photos in `report/photos/`. A case says whether a report must be written, the words it must contain (one of each
list, as a prefix in lowercase) and the words it must not.
"""

# TODO: Il faut setup du LLM as Judge ici + faire un vrai dataset avec des images etc.. Trop long pour une demo

import base64
import mimetypes
import tomllib
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.context import FlowContext, Issue, Language
from interactive_support_flow_api.model.message import Bucket, GeneratedText, TextCode
from interactive_support_flow_damaged.report import (
    DamagePhoto,
    DamageReport,
    analyze_photo,
    correct_report,
)
from interactive_support_flow_eval import Case, evaluate


class Refused(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report: str
    correction: str


class Sent(BaseModel):
    """
    What the customer sent: a photo, then a correction of the report they refused, if any.
    """

    model_config = ConfigDict(extra="forbid")

    photo: str
    refused: Refused | None = None


class Expected(BaseModel):
    # a misspelt key would silently become an empty expectation
    model_config = ConfigDict(extra="forbid")

    report: bool
    mentions: list[list[str]] = []
    avoids: list[str] = []


class ReportCase(Sent):
    expected: Expected


class Group(BaseModel):
    cases: list[ReportCase]


class NothingSaid(Bucket):
    def add_code(self, code: TextCode) -> None:
        raise AssertionError(f"EVAL_UNEXPECTED_MESSAGE:{code}")

    def add_generated(self, text: GeneratedText) -> None:
        raise AssertionError(f"EVAL_UNEXPECTED_MESSAGE:{text.text}")


def read_cases(folder: Path) -> list[Case[Sent, Expected]]:
    cases: list[Case[Sent, Expected]] = []
    for path in sorted(folder.glob("*.toml")):
        try:
            group = Group.model_validate(tomllib.loads(path.read_text()))
        except Exception as error:
            raise AssertionError(f"EVAL_CASE_INVALID:{path.name}:{error}") from None

        for case in group.cases:
            if not (folder / "photos" / case.photo).is_file():
                raise AssertionError(f"EVAL_CASE_INVALID:{path.name}:{case.photo}")
            cases.append(
                Case(
                    input=Sent(photo=case.photo, refused=case.refused),
                    expected=case.expected,
                    group=path.stem,
                )
            )

    return cases


def data_url(photo: Path) -> str:
    """
    The photo as the flow receives it from the customer.
    """
    mime, _ = mimetypes.guess_type(photo.name)
    return f"data:{mime};base64,{base64.b64encode(photo.read_bytes()).decode()}"


def write_report(photos: Path, sent: Sent) -> str | None:
    """
    None when the flow sees no damage (NO_DAMAGE_VISIBLE).
    """
    ctx = FlowContext(
        issue=Issue.DAMAGED, order_number="#CMA_004", language=Language.FR
    )
    photo = data_url(photos / sent.photo)
    try:
        if sent.refused is None:
            analyze_photo(ctx, photo, NothingSaid())
        else:
            ctx.set_extension(DamagePhoto(photo=photo))
            ctx.set_extension(DamageReport(text=sent.refused.report))
            correct_report(ctx, sent.refused.correction, NothingSaid())
    except InvalidAnswer:
        return None
    return ctx.require_extension(DamageReport).text


def mentions(report: str | None, expected: Expected) -> bool:
    text = (report or "").casefold()
    return all(any(word in text for word in words) for words in expected.mentions)


def avoids(report: str | None, expected: Expected) -> bool:
    text = (report or "").casefold()
    return not any(word in text for word in expected.avoids)


@pytest.mark.eval
def test_write_report(request: pytest.FixtureRequest):
    folder = request.path.parent / "report"
    evaluate(
        "damaged.write_report",
        read_cases(folder),
        run=lambda sent: write_report(folder / "photos", sent),
        criteria={
            "report": lambda report, expected: (report is not None) is expected.report,
            "mentions": mentions,
            "avoids": avoids,
        },
    )
