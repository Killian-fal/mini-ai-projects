import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from store import StoreError

from api.routes import overview, pages, runs


def operation_id(route: APIRoute) -> str:
    return route.name


app = FastAPI(title="Sentinel", generate_unique_id_function=operation_id)
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"]
)
for router in (overview.router, pages.router, runs.router):
    app.include_router(router, prefix="/api")


@app.exception_handler(StoreError)
def database_down(_: Request, e: StoreError) -> JSONResponse:
    # the message may hold the Mongo URL and its password: logged, never sent
    logging.getLogger(__name__).error("store: %s", e)
    return JSONResponse({"detail": "base de données indisponible"}, status.HTTP_503_SERVICE_UNAVAILABLE)
