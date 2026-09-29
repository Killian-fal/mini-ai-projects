import gzip
import io
import sys
import threading
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import duckdb
import pytest
import store
from cli import scan
from commoncrawl import index, warc
from pymongo.collection import Collection
from warcio.statusandheaders import StatusAndHeaders
from warcio.warcwriter import WARCWriter

WARC_FILE = "crawl-data/CC-TEST/00000.warc.gz"
PART = "cc-index/table/subset=warc/part-1.parquet"


class CommonCrawl(ThreadingHTTPServer):
    """Local data.commoncrawl.org: serves files, HEAD and Range included, and counts WARC reads."""

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), _Handler)
        self.files: dict[str, bytes] = {}
        self.warc_reads = 0


class _Handler(BaseHTTPRequestHandler):
    server: CommonCrawl

    def do_HEAD(self) -> None:
        self._send(head=True)

    def do_GET(self) -> None:
        self._send(head=False)

    def _send(self, *, head: bool) -> None:
        path = self.path.lstrip("/")
        self.server.warc_reads += path == WARC_FILE
        body = self.server.files.get(path)
        if body is None:
            self.send_error(404)
            return
        if rng := self.headers["Range"]:
            start, end = map(int, rng.removeprefix("bytes=").split("-"))
            body = body[start : end + 1]
        self.send_response(206 if rng else 200)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def log_message(self, *_: object) -> None:
        pass


@pytest.fixture
def cc(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, db: Collection[dict[str, Any]]
) -> Iterator[CommonCrawl]:
    db.delete_many({})
    server = CommonCrawl()
    threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}"
    monkeypatch.setattr(index, "BASE", url)
    monkeypatch.setattr(warc, "BASE", url)
    monkeypatch.setattr(scan, "CRAWL", "CC-TEST")
    monkeypatch.chdir(tmp_path)  # no tranco.csv here
    paths = f"cc-index/table/subset=warc/part-0.parquet\n{PART}"
    server.files["crawl-data/CC-TEST/cc-index-table.paths.gz"] = gzip.compress(paths.encode())
    yield server
    server.shutdown()
    server.server_close()


@pytest.fixture
def crawl(cc: CommonCrawl, tmp_path: Path) -> Callable[..., None]:
    """Serves a WARC holding one html page per url, and the index part pointing to it."""

    def publish(*urls: str) -> None:
        blobs = [_record(url) for url in urls]
        cc.files[WARC_FILE] = b"".join(blobs)
        db = duckdb.connect()
        db.execute("""CREATE TABLE t (url TEXT, url_surtkey TEXT, url_host_name TEXT,
            url_host_registered_domain TEXT, url_host_tld TEXT, url_path TEXT, warc_filename TEXT,
            warc_record_offset BIGINT, warc_record_length BIGINT, fetch_status INT,
            content_mime_detected TEXT, content_languages TEXT)""")
        for i, url in enumerate(urls):
            host, path = urlsplit(url).hostname or "", urlsplit(url).path
            offset = sum(map(len, blobs[:i]))
            db.execute(
                "INSERT INTO t VALUES (?, ?, ?, ?, 'fr', ?, ?, ?, ?, 200, 'text/html', 'fra')",
                [url, f"fr,{host}){path}", host, host, path, WARC_FILE, offset, len(blobs[i])],
            )
        db.execute(f"COPY t TO '{tmp_path / 'part.parquet'}' (FORMAT parquet)")
        cc.files[PART] = (tmp_path / "part.parquet").read_bytes()

    return publish


def _record(url: str) -> bytes:
    buf = io.BytesIO()
    w = WARCWriter(buf, gzip=True)
    html = f"<p>{url}</p>".encode()
    headers = StatusAndHeaders("200 OK", [("Content-Type", "text/html")], protocol="HTTP/1.1")
    w.write_record(
        w.create_warc_record(
            url, "response", payload=io.BytesIO(html), length=len(html), http_headers=headers
        )
    )
    return buf.getvalue()


def _scan(monkeypatch: pytest.MonkeyPatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["scan", "--part", "1", "--workers", "1", *args])
    scan.main()


def test_a_scan_stores_the_selected_pages_and_skips_them_next_time(
    cc: CommonCrawl, crawl: Callable[..., None], monkeypatch: pytest.MonkeyPatch
) -> None:
    crawl("https://a.fr/jobs/1", "https://b.fr/blog")
    _scan(monkeypatch)
    stored = {p.url: p.bucket for p in store.iter_pages()}
    assert stored == {"https://a.fr/jobs/1": "hiring", "https://b.fr/blog": "other"}
    reads = cc.warc_reads
    _scan(monkeypatch)
    assert cc.warc_reads == reads


def test_consecutive_download_failures_stop_the_scan_with_the_blocked_code(
    cc: CommonCrawl, crawl: Callable[..., None], monkeypatch: pytest.MonkeyPatch
) -> None:
    crawl(*(f"https://s{i}.fr/" for i in range(6)))
    del cc.files[WARC_FILE]
    monkeypatch.setattr(scan, "BLOCKED_AFTER", 2)
    with pytest.raises(SystemExit) as stop:
        _scan(monkeypatch)
    assert stop.value.code == scan.BLOCKED_EXIT
    assert cc.warc_reads < 6
