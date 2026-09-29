from collections.abc import Callable

import store
from fastapi.testclient import TestClient

Page = Callable[..., str]
Detect = Callable[..., None]


def test_an_empty_base_gives_zeros(client: TestClient) -> None:
    body = client.get("/api/overview").json()

    assert body == {
        "stored": 0,
        "analysed": 0,
        "flagged": 0,
        "runs": 0,
        "input_tokens": 0,
        "cost_usd": 0,
        "threshold": None,
        "histogram": [0] * 20,
        "buckets": [],
        "latest_flagged": [],
    }


def test_the_overview_counts_pages_scores_and_buckets(client: TestClient, page: Page, detect: Detect) -> None:
    detect(page("https://a.example/1"), 0.96)
    detect(page("https://b.example/2", bucket="control"), 0.03)
    detect(page("https://c.example/3", crawl="CC-MAIN-2026-30"), 0.5, usage=store.Usage(500, 1))
    page("https://d.example/4")

    body = client.get("/api/overview").json()

    assert (body["stored"], body["analysed"], body["flagged"]) == (4, 3, 1)
    assert (body["histogram"][0], body["histogram"][10], body["histogram"][19]) == (1, 1, 1)
    assert body["buckets"] == [
        {"bucket": "control", "count": 1, "flagged": 0},
        {"bucket": "hiring", "count": 3, "flagged": 1},
    ]
    assert [(p["url"], p["score"]) for p in body["latest_flagged"]] == [("https://a.example/1", 0.96)]


def test_the_cost_counts_every_detection_of_a_page(client: TestClient, page: Page, detect: Detect) -> None:
    page_id = page("https://a.example/")
    detect(page_id, 0.1)
    detect(page_id, 0.2)
    detect(page("https://b.example/"), 0.3, usage=store.Usage(500, 1))

    body = client.get("/api/overview").json()

    assert body["input_tokens"] == 2_500
    assert body["cost_usd"] == 2_500 / 1e6 * 0.042


def test_runs_are_counted_per_crawl(client: TestClient, page: Page, detect: Detect) -> None:
    detect(page("https://a.example/1"), 0.9)
    detect(page("https://b.example/2"), 0.1)
    detect(page("https://c.example/3", crawl="CC-MAIN-2026-30"), 0.6, model="jev-2")

    assert client.get("/api/overview").json()["runs"] == 2
    assert client.get("/api/overview", params={"crawl": "CC-MAIN-2026-30"}).json()["runs"] == 1


def test_the_overview_filters_by_crawl(client: TestClient, page: Page, detect: Detect) -> None:
    detect(page("https://a.example/1"), 0.96)
    page("https://c.example/3", crawl="CC-MAIN-2026-30")

    body = client.get("/api/overview", params={"crawl": "CC-MAIN-2026-30"}).json()

    assert (body["stored"], body["analysed"], body["flagged"]) == (1, 0, 0)


def test_crawls_are_listed_once_sorted(client: TestClient, page: Page) -> None:
    page("https://a.example/1")
    page("https://b.example/2", crawl="CC-MAIN-2026-30")
    page("https://c.example/3", crawl="CC-MAIN-2026-30")

    assert client.get("/api/crawls").json() == {"crawls": ["CC-MAIN-2026-30", "CC-MAIN-2026-34"]}


def test_the_threshold_is_the_latest_detection_one(client: TestClient, page: Page, detect: Detect) -> None:
    detect(page("https://a.example/1"), 0.1, threshold=0.5)
    detect(page("https://b.example/2"), 0.1, threshold=0.9)

    assert client.get("/api/overview").json()["threshold"] == 0.9


def test_a_failed_detection_stays_out_of_the_histogram(
    client: TestClient, page: Page, detect: Detect
) -> None:
    detect(page("https://err.example/"), None, error="503")
    detect(page("https://ok.example/"), 0.96)

    body = client.get("/api/overview").json()

    assert body["histogram"][19] == 1
    assert [p["url"] for p in body["latest_flagged"]] == ["https://ok.example/"]
