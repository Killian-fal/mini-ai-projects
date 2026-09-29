import gzip
import io
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import duckdb
import pytest
from commoncrawl import CommonCrawlError, IndexRow, fetch_page, index, index_parts, read_index, warc
from warcio.statusandheaders import StatusAndHeaders
from warcio.warcwriter import WARCWriter

CRAWL = "CC-MAIN-TEST"
WARC_FILE = "crawl-data/CC-MAIN-TEST/segments/1/warc/00000.warc.gz"


class CommonCrawl(ThreadingHTTPServer):
    """Local data.commoncrawl.org: serves files (Range included) and fails on demand."""

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), _Handler)
        self.files: dict[str, bytes] = {}
        self.faults: list[int | None] = []  # failures before success: HTTP code, None = cut
        self.hits = 0

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"


class _Handler(BaseHTTPRequestHandler):
    server: CommonCrawl

    def do_GET(self) -> None:
        self.server.hits += 1
        if self.server.faults:
            fault = self.server.faults.pop(0)
            if fault is None:  # announces 10 bytes, sends 1: IncompleteRead on the client side
                self.send_response(200)
                self.send_header("Content-Length", "10")
                self.end_headers()
                self.wfile.write(b"x")
                self.close_connection = True
            else:
                self.send_error(fault)
            return
        body = self.server.files.get(self.path.lstrip("/"))
        if body is None:
            self.send_error(404)
            return
        if rng := self.headers["Range"]:
            start, end = map(int, rng.removeprefix("bytes=").split("-"))
            body = body[start : end + 1]
        self.send_response(206 if rng else 200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_: object) -> None:
        pass


@pytest.fixture
def cc(monkeypatch: pytest.MonkeyPatch) -> Iterator[CommonCrawl]:
    server = CommonCrawl()
    threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True).start()
    monkeypatch.setattr(index, "BASE", server.url)
    monkeypatch.setattr(warc, "BASE", server.url)
    monkeypatch.setattr(time, "sleep", lambda _: None)
    yield server
    server.shutdown()
    server.server_close()


def _record(url: str, rec_type: str, html: str = "") -> bytes:
    buf = io.BytesIO()
    w = WARCWriter(buf, gzip=True)
    headers = StatusAndHeaders("200 OK", [("Content-Type", "text/html")], protocol="HTTP/1.1")
    w.write_record(
        w.create_warc_record(
            url,
            rec_type,
            payload=io.BytesIO(payload := html.encode()),
            length=len(payload),
            http_headers=headers if rec_type == "response" else None,
        )
    )
    return buf.getvalue()


@pytest.fixture
def crawl(cc: CommonCrawl, tmp_path: Path) -> Path:
    """A 3-record WARC served by `cc`, and the parquet index part pointing to it."""
    records = [
        ("https://www.exemple.fr/", "response", "<p>Bonjour</p>"),
        ("https://www.exemple.fr/a", "metadata", "fetchTimeMs: 12"),  # no response: CommonCrawlError
        ("https://exemple.fr/b", "response", "<p>Été</p>"),
    ]
    blobs = [_record(*r) for r in records]
    cc.files[WARC_FILE] = b"".join(blobs)
    offsets = [sum(map(len, blobs[:i])) for i in range(len(blobs))]

    def row(
        url: str, off: int, status: int = 200, mime: str = "text/html", langs: str = "fra"
    ) -> tuple[object, ...]:
        path = url.split("exemple.fr", 1)[1]
        return (url, f"fr,exemple){path}", "www.exemple.fr", "exemple.fr", "fr", path,
                WARC_FILE, offsets[off], len(blobs[off]), status, mime, langs)  # fmt: skip

    rows = [
        row("https://www.exemple.fr/", 0, langs="eng,fra"),
        row("https://www.exemple.fr/a", 1),
        row("https://exemple.fr/b", 2, mime="application/xhtml+xml"),
        row("https://exemple.fr/pdf", 2, mime="application/pdf"),
        row("https://exemple.fr/404", 2, status=404),
        row("https://exemple.fr/en", 2, langs="eng"),
    ]
    part = tmp_path / "part-00000.parquet"
    db = duckdb.connect()
    db.execute("""CREATE TABLE t (url TEXT, url_surtkey TEXT, url_host_name TEXT,
        url_host_registered_domain TEXT, url_host_tld TEXT, url_path TEXT, warc_filename TEXT,
        warc_record_offset BIGINT, warc_record_length BIGINT, fetch_status INT,
        content_mime_detected TEXT, content_languages TEXT)""")
    db.executemany("INSERT INTO t VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    db.execute(f"COPY t TO '{part}' (FORMAT parquet)")
    return part


def test_index_parts_lists_only_the_warc_subset(cc: CommonCrawl) -> None:
    paths = ["cc-index/table/subset=warc/part-0.parquet", "cc-index/table/subset=robotstxt/part-0.parquet"]
    cc.files[f"crawl-data/{CRAWL}/cc-index-table.paths.gz"] = gzip.compress("\n".join(paths).encode())
    assert index_parts(CRAWL) == [f"{cc.url}/cc-index/table/subset=warc/part-0.parquet"]


def test_read_index_keeps_html_pages_in_the_requested_languages(
    crawl: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(index, "BATCH", 1)  # force several batches
    rows = list(read_index(str(crawl), ("fra",)))
    assert [r.url for r in rows] == [
        "https://www.exemple.fr/",
        "https://www.exemple.fr/a",
        "https://exemple.fr/b",
    ]
    assert rows[0].site == "fr,exemple"
    assert len(list(read_index(str(crawl), ("fra",), rows=2))) == 2


def test_fetch_page_reads_the_record_the_index_points_to(crawl: Path) -> None:
    home, no_response, b = read_index(str(crawl), ("fra",))
    assert fetch_page(home).html == "<p>Bonjour</p>"
    assert "text/html" in fetch_page(b).headers
    assert fetch_page(b).html == "<p>Été</p>"
    with pytest.raises(CommonCrawlError):
        fetch_page(no_response)


@pytest.fixture
def home(crawl: Path) -> IndexRow:
    return next(read_index(str(crawl), ("fra",)))


def test_transient_failures_are_retried(cc: CommonCrawl, home: IndexRow) -> None:
    cc.faults = [503, None, 429]
    assert fetch_page(home).html == "<p>Bonjour</p>"
    assert cc.hits == 4


def test_a_permanent_error_is_not_retried(cc: CommonCrawl, home: IndexRow) -> None:
    cc.faults = [403]
    with pytest.raises(CommonCrawlError):
        fetch_page(home)
    assert cc.hits == 1


def test_gives_up_after_the_last_retry(cc: CommonCrawl, home: IndexRow) -> None:
    cc.faults = [503] * warc.RETRIES
    with pytest.raises(CommonCrawlError):
        fetch_page(home)
    assert cc.hits == warc.RETRIES


def test_an_unreadable_index_part_raises_a_commoncrawl_error(tmp_path: Path) -> None:
    (part := tmp_path / "part.parquet").write_bytes(b"not parquet")
    with pytest.raises(CommonCrawlError):
        list(read_index(str(part), ("fra",)))


def test_a_corrupt_warc_record_raises_a_commoncrawl_error(cc: CommonCrawl, home: IndexRow) -> None:
    cc.files[WARC_FILE] = gzip.compress(b"x" * 500)[:40]
    with pytest.raises(CommonCrawlError):
        fetch_page(home)
