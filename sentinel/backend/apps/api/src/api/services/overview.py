import store


def crawls() -> list[str]:
    return store.crawls()


def overview(crawl: str | None) -> store.Overview:
    return store.overview(crawl)
