import store

from api.schema import PageQuery


def listed(query: PageQuery) -> store.PageList:
    run = None
    if query.run is not None:
        run = store.RunKey.parse(query.run)
        if run is None:
            return store.PageList(items=[], total=0, flagged_total=0)
    filters = store.PageFilters(
        q=query.q,
        buckets=query.bucket,
        crawl=query.crawl,
        run=run,
        flagged_only=query.flagged_only,
        with_error=query.with_error,
        min_score=query.min_score,
    )
    return store.list_pages(filters, query.sort, query.order, query.page, query.size)


def get(page_id: str) -> store.PageDetail | None:
    return store.get_page(page_id)


def html(page_id: str) -> str | None:
    return store.page_html(page_id)


def request(page_id: str) -> str | None:
    return store.page_request(page_id)
