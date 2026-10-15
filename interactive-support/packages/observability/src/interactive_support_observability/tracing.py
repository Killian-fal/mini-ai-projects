import os
from contextlib import contextmanager

import mlflow
import mlflow.dspy as mlflow_dspy
import mlflow.tracing as mlflow_tracing


def init_observability(experiment: str = "interactive-support"):
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment(experiment)
    mlflow_dspy.autolog()


@contextmanager
def trace_session(session_id: str):
    with mlflow_tracing.context(session_id=session_id):
        yield
