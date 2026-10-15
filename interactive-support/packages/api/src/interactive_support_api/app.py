from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from interactive_support_api.route import conversation
from interactive_support_api.exception import ApiError

app = FastAPI(
    title="interactive-support", generate_unique_id_function=lambda route: route.name
)
app.include_router(conversation.router)


@app.exception_handler(ApiError)
async def api_error(request: Request, e: ApiError) -> JSONResponse:
    if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        raise e
    return JSONResponse({"detail": str(e)}, status_code=e.status_code)


@app.exception_handler(Exception)
async def unexpected_error(request: Request, e: Exception) -> JSONResponse:
    return JSONResponse(
        {"detail": "INTERNAL_ERROR"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
