from fastapi import APIRouter

from api.mappers.overview import crawls, overview
from api.schema import Crawls, Overview
from api.services import overview as service

router = APIRouter()


@router.get("/crawls")
def list_crawls() -> Crawls:
    return crawls(service.crawls())


@router.get("/overview")
def get_overview(crawl: str | None = None) -> Overview:
    return overview(service.overview(crawl))
