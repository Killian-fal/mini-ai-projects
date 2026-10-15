from pydantic import Field

import interactive_support_domain_order as orders
from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.tools import llm
from interactive_support_flow_api.model.context import Extension, FlowContext, Language
from interactive_support_flow_api.model.message import Bucket
from interactive_support_flow_api.model.question import ConfirmationQuestion
from interactive_support_flow_damaged.code import DamagedCode


class DamagePhoto(Extension):
    __key__ = "damage_photo"

    photo: str


class DamageReport(Extension):
    __key__ = "damage_report"

    text: str


class ReportInput(llm.GenerateInput):
    photo: llm.Image = Field(
        description="The photo the customer took of their damaged order"
    )
    refused_report: str | None = Field(
        description="The report we proposed and the customer refused, None the first time"
    )
    correction: str | None = Field(
        description="What the customer wants changed in refused_report, None the first time"
    )
    language: Language = Field(
        description="Language the report must be written in: the customer reads it before it is sent"
    )


class WrittenReport(llm.GenerateOutput):
    report: str | None = Field(
        description="1 to 3 sentences for the support team: the damaged product, the damage, where it is and how bad. "
        "refused_report with the correction applied when there is one. None if the photo shows no damaged product"
    )


def analyze_photo(ctx: FlowContext, photo: str, bucket: Bucket) -> None:
    ctx.set_extension(DamagePhoto(photo=photo))
    _write_report(ctx, refused_report=None, correction=None)


def correct_report(ctx: FlowContext, correction: str, bucket: Bucket) -> None:
    refused = ctx.require_extension(DamageReport).text
    _write_report(ctx, refused_report=refused, correction=correction)


def _write_report(
    ctx: FlowContext, refused_report: str | None, correction: str | None
) -> None:
    result = llm.generate(
        "Describe the damage on the photo of the customer's order. Never invent a damage the photo doesn't show or the customer doesn't state.",
        ReportInput(
            photo=llm.Image(ctx.require_extension(DamagePhoto).photo),
            refused_report=refused_report,
            correction=correction,
            language=ctx.language,
        ),
        WrittenReport,
    )
    if result.report is None:
        raise InvalidAnswer(DamagedCode.NO_DAMAGE_VISIBLE)
    ctx.set_extension(DamageReport(text=result.report))


def report_confirmation(ctx: FlowContext) -> ConfirmationQuestion:
    return ConfirmationQuestion(value=ctx.require_extension(DamageReport).text)


def send_to_support(ctx: FlowContext, bucket: Bucket) -> None:
    damage = orders.Damage(
        photo=ctx.require_extension(DamagePhoto).photo,
        report=ctx.require_extension(DamageReport).text,
    )
    orders.report_damage(ctx.order_number, damage)
    bucket.add_code(DamagedCode.SENT_TO_SUPPORT)
