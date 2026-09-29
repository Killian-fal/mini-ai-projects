from typing import Any

from bson import ObjectId
from pymongo.collection import Collection
from store import iter_pages, page_html, save_page


def test_the_html_lives_apart_from_the_page_document(db: Collection[dict[str, Any]]) -> None:
    db.delete_many({})
    page_id = save_page("https://a.test/x", "control", "c", "", "<p>é</p>")
    assert page_id is not None

    stored = db.find_one({"_id": ObjectId(page_id)}, {"html": 1})
    assert stored is not None
    assert "html" not in stored
    assert page_html(page_id) == "<p>é</p>"
    assert [p.html for p in iter_pages()] == ["<p>é</p>"]


def test_a_page_whose_html_is_missing_is_skipped(db: Collection[dict[str, Any]]) -> None:
    db.delete_many({})
    page_id = save_page("https://a.test/x", "control", "c", "", "<p>a</p>")
    assert page_id is not None
    db.database["html"].delete_one({"_id": ObjectId(page_id)})

    assert list(iter_pages()) == []
    assert page_html(page_id) is None
