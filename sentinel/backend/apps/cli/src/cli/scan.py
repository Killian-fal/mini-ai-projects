import argparse
import random
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from commoncrawl import CommonCrawlError, Page, fetch_page, index_parts, read_index
from store import known_urls, save_page

from cli.select import Candidate, candidates, tranco

CRAWL = "CC-MAIN-2026-34"
LANGUAGES = ("eng", "fra")
BLOCKED_EXIT = 2
BLOCKED_AFTER = 20


def main() -> None:
    a = _parse()
    parts = index_parts(CRAWL)
    chosen = a.part or random.sample(range(1, len(parts)), a.parts)  # part 0 is blogspot.com only
    quota = max(1, a.limit // len(chosen))
    bands = tranco(a.tranco_top)
    saved: Counter[str] = Counter()
    pool = ThreadPoolExecutor(a.workers)
    try:
        for part in chosen:
            print(f"\npart {part}/{len(parts)}")
            try:
                todo = candidates(read_index(parts[part], LANGUAGES, a.rows), bands, quota)
            except CommonCrawlError as e:
                print(f"! {e}: {e.__cause__}")
                continue
            done = known_urls([c.row.url for c in todo])
            todo = [c for c in todo if c.row.url not in done]
            print(f"{len(done)} déjà en base, {len(todo)} pages sélectionnées")
            _download(pool, todo, saved)
    finally:
        pool.shutdown(cancel_futures=True)
        print("\nbucket        pages")
        for bucket, n in sorted(saved.items()):
            print(f"{bucket:12}  {n:6}")


def _parse() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Sélectionne des pages Common Crawl et stocke leur HTML brut.")
    ap.add_argument("--part", type=int, action="append", help="part(s) d'index (1-299), répétable")
    ap.add_argument("--parts", type=int, default=1, help="parts tirées au hasard si --part est absent")
    ap.add_argument("--rows", type=int, help="lignes d'index lues max par part, toute la part par défaut")
    ap.add_argument("--limit", type=int, default=2000, help="pages téléchargées max, réparties entre parts")
    ap.add_argument("--workers", type=int, default=4, help="téléchargements en parallèle")
    ap.add_argument("--tranco-top", type=int, default=100_000)
    return ap.parse_args()


def _download(pool: ThreadPoolExecutor, todo: list[Candidate], saved: Counter[str]) -> None:
    failed = 0
    for i, (c, page) in enumerate(zip(todo, pool.map(_fetch, todo), strict=True), 1):
        if i % 100 == 0:
            print(f"{i}/{len(todo)}", flush=True)
        if isinstance(page, CommonCrawlError):
            print(f"! {page}: {page.__cause__}")
            failed += 1
            if failed >= BLOCKED_AFTER:
                print(f"! {failed} échecs d'affilée, Common Crawl nous bloque sans doute : arrêt")
                raise SystemExit(BLOCKED_EXIT)  # tools/scan_all.sh pauses, then retries the part
            continue
        failed = 0
        if save_page(c.row.url, c.bucket, CRAWL, page.headers, page.html, tranco=c.band):
            saved[c.bucket] += 1


def _fetch(c: Candidate) -> Page | CommonCrawlError:
    try:
        return fetch_page(c.row)
    except CommonCrawlError as e:
        return e
