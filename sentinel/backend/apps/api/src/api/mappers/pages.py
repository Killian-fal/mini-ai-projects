import json
from dataclasses import asdict

import store

from api.schema import PageDetail, PageHtml, PageList, PageRequest, PageRow


def page_row(row: store.PageRow) -> PageRow:
    return PageRow(**asdict(row))


def page_list(pages: store.PageList) -> PageList:
    return PageList(
        items=[page_row(i) for i in pages.items], total=pages.total, flagged_total=pages.flagged_total
    )


def page_detail(page: store.PageDetail) -> PageDetail:
    return PageDetail(**asdict(page))


def page_html(html: str) -> PageHtml:
    return PageHtml(html=html)


def page_request(body: str) -> PageRequest:
    return PageRequest(request=json.loads(body))
