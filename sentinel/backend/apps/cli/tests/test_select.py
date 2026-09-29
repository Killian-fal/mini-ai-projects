from cli.select import MID, PER_SITE, UNRANKED, candidates
from commoncrawl import IndexRow


def _rows(site: str, n: int, domain: str = "", path: str = "/jobs/") -> list[IndexRow]:
    return [
        IndexRow(f"https://{site}{path}{i}", site, site, domain or site, "com", f"{path}{i}", "w", 0, 1)
        for i in range(n)
    ]


def test_every_site_gives_at_most_ten_pages_and_the_top_100k_none() -> None:
    rows = [*_rows("one", 1), *_rows("shop", 15), *_rows("big", 5, "top.com"), *_rows("b", 4)]
    picked = candidates(iter(rows), {"top.com": "top_100k", "b": MID}, limit=50)
    assert [c.row.site for c in picked] == ["one"] + ["shop"] * PER_SITE + ["b"] * 4
    assert picked[-1].band == MID
    assert {c.band for c in picked} == {UNRANKED, MID}
    assert len(candidates(iter(rows), {}, limit=3)) == 3


def test_pages_matching_no_category_are_kept_as_other() -> None:
    picked = candidates(iter(_rows("blog", 2, path="/2026/hello-world-")), {}, limit=10)
    assert [c.bucket for c in picked] == ["other", "other"]
