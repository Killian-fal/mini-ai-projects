import mlflow
from fastapi import FastAPI

from audio_api.environment import (
    ENABLE_MLFLOW,
    MLFLOW_EXPERIMENT_NAME_ENV,
    MLFLOW_TRACKING_URI_ENV,
)
from audio_api.exception_handlers import init_exception_handlers


def create_app() -> FastAPI:
    fastapi = FastAPI(
        title="Agent Audio API",
        description="API for interacting with the Agent Audio service",
        version="1.0.0"
    )

    _init_mlflow()
    _init_routers(fastapi)
    init_exception_handlers(fastapi)

    return fastapi


def _init_routers(fastapi: FastAPI):
    from audio_api.audio.router import audio_router

    fastapi.include_router(audio_router)


def _init_mlflow():
    if not ENABLE_MLFLOW:
        mlflow.tracing.disable()
        return

    if not MLFLOW_TRACKING_URI_ENV or not MLFLOW_EXPERIMENT_NAME_ENV:
        raise ValueError(
            "MLflow tracking URI (MLFLOW_TRACKING_URI) and experiment name (MLFLOW_EXPERIMENT_NAME) must be set in environment variables."
        )

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI_ENV)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME_ENV)
    mlflow.autolog()
