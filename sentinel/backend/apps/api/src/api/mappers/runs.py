import store

from api.mappers.overview import cost_usd
from api.schema import Daily, Run, Runs


def runs(rows: list[store.Run], days: list[store.DayCount]) -> Runs:
    return Runs(runs=[_run(r) for r in rows], daily=[_daily(d) for d in days])


def _run(r: store.Run) -> Run:
    return Run(
        id=r.key.id,
        started_at=r.key.minute,
        model=r.key.model,
        threshold=r.key.threshold,
        analysed=r.analysed,
        flagged=r.flagged,
        errors=r.errors,
        input_tokens=r.input_tokens,
        output_tokens=r.output_tokens,
        cost_usd=cost_usd(r.input_tokens),
        duration_ms=r.duration_ms,
        median_latency_ms=r.median_latency_ms,
    )


def _daily(d: store.DayCount) -> Daily:
    return Daily(day=d.day, analysed=d.analysed, flagged_rate=d.flagged / d.analysed if d.analysed else 0.0)
