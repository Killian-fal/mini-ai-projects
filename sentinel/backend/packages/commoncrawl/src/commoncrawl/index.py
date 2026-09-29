import gzip
from collections.abc import Iterator
from urllib.request import urlopen

import duckdb

from commoncrawl.error import CommonCrawlError
from commoncrawl.model import IndexRow

BASE = "https://data.commoncrawl.org"
BATCH = 10_000


def index_parts(crawl: str) -> list[str]:
    with urlopen(f"{BASE}/crawl-data/{crawl}/cc-index-table.paths.gz", timeout=30) as r:
        paths = gzip.decompress(r.read()).decode().split()
    return [f"{BASE}/{p}" for p in paths if "subset=warc" in p]


def read_index(part: str, languages: tuple[str, ...], rows: int | None = None) -> Iterator[IndexRow]:
    langs = " OR ".join(f"content_languages LIKE '%{lang}%'" for lang in languages)
    limit = f"LIMIT {rows}" if rows else ""
    try:
        cur = duckdb.connect().execute(f"""
        SELECT url, split_part(url_surtkey, ')', 1), url_host_name, url_host_registered_domain,
               url_host_tld, url_path, warc_filename, warc_record_offset, warc_record_length
        FROM read_parquet('{part}')
        WHERE fetch_status = 200
          AND content_mime_detected IN ('text/html', 'application/xhtml+xml')
          AND ({langs})
        {limit}""")
        while batch := cur.fetchmany(BATCH):
            yield from (IndexRow(*r) for r in batch)
    except duckdb.Error as e:
        raise CommonCrawlError(part) from e
