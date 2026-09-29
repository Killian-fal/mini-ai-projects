from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

Page = Callable[..., str]
Detect = Callable[..., None]


def test_runs_group_detections_by_minute_model_and_threshold(
    client: TestClient, page: Page, detect: Detect
) -> None:
    detect(page("https://a.example/"), 0.9)
    detect(page("https://b.example/"), None, error="503", usage=None, answers=None, latency_ms=None)
    detect(page("https://c.example/"), 0.6, threshold=0.5, model="jev-2")

    runs = client.get("/api/runs").json()["runs"]

    assert len(runs) == 2
    main = next(r for r in runs if r["model"] == "jev-latest")
    assert (main["analysed"], main["flagged"], main["errors"]) == (2, 1, 1)
    assert (main["input_tokens"], main["output_tokens"]) == (1000, 10)
    assert main["cost_usd"] == 1000 / 1e6 * 0.042
    assert (main["duration_ms"], main["median_latency_ms"]) == (100, 100)
    assert main["threshold"] == 0.8
    assert main["started_at"].endswith(":00Z")


def test_daily_counts_cover_the_last_30_days(client: TestClient, page: Page, detect: Detect) -> None:
    detect(page("https://a.example/"), 0.9)
    detect(page("https://b.example/"), 0.1)
    detect(page("https://old.example/"), 0.9, at=datetime.now(UTC) - timedelta(days=30))

    daily = client.get("/api/runs").json()["daily"]

    today = datetime.now(UTC).date()
    assert [d["day"] for d in daily] == [str(today - timedelta(days=i)) for i in range(29, -1, -1)]
    assert daily[-1] == {"day": str(today), "analysed": 2, "flagged_rate": 0.5}
    assert sum(d["analysed"] for d in daily) == 2


def test_no_detection_gives_no_run_and_empty_days(client: TestClient) -> None:
    body = client.get("/api/runs").json()

    assert body["runs"] == []
    assert {(d["analysed"], d["flagged_rate"]) for d in body["daily"]} == {(0, 0)}


def test_the_page_list_filters_by_run(client: TestClient, page: Page, detect: Detect) -> None:
    detect(page("https://a.example/"), 0.9)
    detect(page("https://c.example/"), 0.6, threshold=0.5, model="jev-2")
    run = next(r for r in client.get("/api/runs").json()["runs"] if r["model"] == "jev-2")

    body = client.get("/api/pages", params={"run": run["id"]}).json()

    assert [i["url"] for i in body["items"]] == ["https://c.example/"]


def test_an_unknown_run_matches_no_page(client: TestClient, page: Page, detect: Detect) -> None:
    detect(page("https://a.example/"), 0.9)

    assert client.get("/api/pages", params={"run": "n-importe-quoi"}).json()["total"] == 0
