from datetime import UTC, datetime
from typing import Any

import pytest
from pymongo.collection import Collection
from store import Detection, add_detection, iter_pages, known_urls, save_page
from store.pages import write


def test_undetected_pages_come_from_the_partial_index(db: Collection[dict[str, Any]]) -> None:
    db.delete_many({})
    done = save_page("https://a.test/x", "control", "c", "", "<p>a</p>")
    save_page("https://b.test/y", "control", "c", "", "<p>b</p>")
    assert done is not None
    add_detection(
        done, Detection("jev", "[visible] a", ["visible"], 0.1, 0.8, flagged=False, at=datetime.now(UTC))
    )
    assert [p.url for p in iter_pages(undetected=True)] == ["https://b.test/y"]
    assert len(list(iter_pages())) == 2


def test_known_urls_are_looked_up_in_chunks(
    db: Collection[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    db.delete_many({})
    save_page("https://a.test/1", "control", "c", "", "x")
    save_page("https://a.test/3", "control", "c", "", "x")
    monkeypatch.setattr(write, "KNOWN_CHUNK", 2)
    assert known_urls([f"https://a.test/{i}" for i in range(5)]) == {"https://a.test/1", "https://a.test/3"}
