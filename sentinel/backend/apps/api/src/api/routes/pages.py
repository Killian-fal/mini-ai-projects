from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from api.mappers.pages import page_detail, page_html, page_list, page_request
from api.schema import NOT_FOUND, PageDetail, PageHtml, PageList, PageQuery, PageRequest
from api.services import pages as service

router = APIRouter()


@router.get("/pages")
def list_pages(query: Annotated[PageQuery, Query()]) -> PageList:
    return page_list(service.listed(query))


@router.get("/pages/{page_id}", responses=NOT_FOUND)
def get_page(page_id: str) -> PageDetail:
    doc = service.get(page_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "page introuvable")
    return page_detail(doc)


@router.get("/pages/{page_id}/html", responses=NOT_FOUND)
def get_page_html(page_id: str) -> PageHtml:
    html = service.html(page_id)
    if html is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "page introuvable")
    return page_html(html)


@router.get("/pages/{page_id}/request", responses=NOT_FOUND)
def get_page_request(page_id: str) -> PageRequest:
    body = service.request(page_id)
    if body is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "aucune requête stockée")
    return page_request(body)
