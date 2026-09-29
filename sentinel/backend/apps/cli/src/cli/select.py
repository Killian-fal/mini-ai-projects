import csv
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import groupby, islice
from operator import attrgetter
from pathlib import Path

from commoncrawl import IndexRow

BUCKETS = [
    ("hiring", re.compile(r"/(cv|resume|portfolio|apply|careers?|jobs?)(/|$|\.)")),
    ("reputation", re.compile(r"/(reviews?|product|best-|vs-|top-\d+)")),
    ("academic", re.compile(r"/(papers?|publications?|preprint)")),
    ("support", re.compile(r"/(support|faq|pricing|contact)")),
]
CHEAP_TLD = {"xyz", "top", "info", "online", "site"}
OTHER = "other"
TOP = "top_100k"
MID = "100k_1m"
UNRANKED = "unranked"
PER_SITE = 10


@dataclass(frozen=True, slots=True)
class Candidate:
    row: IndexRow
    bucket: str
    band: str


def tranco(top: int, path: Path = Path("tranco.csv")) -> dict[str, str]:
    """Domain → Tranco band. A domain missing from the file ranks beyond 1M: unranked."""
    if not path.exists():
        print(f"! {path} absent, pas d'exclusion des gros sites (https://tranco-list.eu/top-1m.csv.zip)")
        return {}
    with path.open() as f:
        return {dom.strip(): (TOP if int(rank) <= top else MID) for rank, dom in csv.reader(f)}


def candidates(rows: Iterable[IndexRow], bands: dict[str, str], limit: int) -> list[Candidate]:
    out: list[Candidate] = []
    # the index is sorted by SURT, so a site's rows are contiguous
    for _, site in groupby(rows, key=attrgetter("site")):
        out += _site(site, bands)
        if len(out) >= limit:
            return out[:limit]
    return out


def _site(rows: Iterator[IndexRow], bands: dict[str, str]) -> list[Candidate]:
    picked = []
    for row in islice(rows, PER_SITE):
        band = bands.get(row.domain, UNRANKED)
        if band == TOP:
            return []
        picked.append(Candidate(row, _bucket(row), band))
    return picked


def _bucket(row: IndexRow) -> str:
    for name, pat in BUCKETS:
        if pat.search(row.path):
            return name
    return "cheap_tld" if row.tld in CHEAP_TLD else OTHER
