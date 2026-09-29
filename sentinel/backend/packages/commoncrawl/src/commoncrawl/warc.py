import io
import random
import time
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from warcio.archiveiterator import ArchiveIterator
from warcio.exceptions import ArchiveLoadFailed

from commoncrawl.error import CommonCrawlError
from commoncrawl.index import BASE
from commoncrawl.model import IndexRow, Page

RETRIES = 5
RETRY_CODES = {429, 500, 502, 503, 504}


def fetch_page(row: IndexRow) -> Page:
    req = Request(
        f"{BASE}/{row.warc_file}", headers={"Range": f"bytes={row.offset}-{row.offset + row.length - 1}"}
    )
    try:
        raw = _read(req)
    except (OSError, HTTPException) as e:
        raise CommonCrawlError(row.url) from e
    try:
        for rec in ArchiveIterator(io.BytesIO(raw)):
            if rec.rec_type == "response":
                return Page(str(rec.http_headers), rec.content_stream().read().decode("utf-8", "replace"))
    except ArchiveLoadFailed as e:
        raise CommonCrawlError(row.url) from e
    raise CommonCrawlError(row.url)


def _read(req: Request) -> bytes:
    """GET with backoff (1, 2, 4, 8 s + jitter)"""
    for attempt in range(RETRIES):
        if attempt:
            time.sleep(2 ** (attempt - 1) + random.random())
        try:
            with urlopen(req, timeout=30) as r:
                data: bytes = r.read()
                return data
        except HTTPError as e:
            e.close()
            if e.code not in RETRY_CODES or attempt == RETRIES - 1:
                raise
        except (OSError, HTTPException):
            if attempt == RETRIES - 1:
                raise
    raise AssertionError  # unreachable: the last attempt returns or raises
