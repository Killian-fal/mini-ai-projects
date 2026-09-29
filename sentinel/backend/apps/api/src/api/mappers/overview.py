from dataclasses import asdict

import store

from api.mappers.pages import page_row
from api.schema import BucketCount, Crawls, Overview

USD_PER_MILLION_INPUT_TOKENS = 0.042


def cost_usd(input_tokens: int) -> float:
    return input_tokens / 1_000_000 * USD_PER_MILLION_INPUT_TOKENS


def crawls(names: list[str]) -> Crawls:
    return Crawls(crawls=names)


def overview(o: store.Overview) -> Overview:
    return Overview(
        stored=o.stored,
        analysed=o.analysed,
        flagged=o.flagged,
        runs=o.runs,
        input_tokens=o.input_tokens,
        cost_usd=cost_usd(o.input_tokens),
        threshold=o.threshold,
        histogram=o.histogram,
        buckets=[BucketCount(**asdict(b)) for b in o.buckets],
        latest_flagged=[page_row(p) for p in o.latest_flagged],
    )
