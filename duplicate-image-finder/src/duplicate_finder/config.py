from dataclasses import dataclass
from pathlib import Path

import yaml


DEFAULT_BATCH_SIZE = 16
DEFAULT_NUM_WORKERS = 2
DEFAULT_SIMILARITY_THRESHOLD = 0.10
DEFAULT_MAX_NEIGHBORS = 50


@dataclass(frozen=True)
class Config:
    folder: Path
    db_path: Path
    batch_size: int
    num_workers: int
    similarity_threshold: float
    max_neighbors: int
    agent_workspace: Path
    agent_model_id: str
    agent_url: str


def load_config(path: Path) -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return Config(
        folder=Path(data["folder"]),
        db_path=Path(data["db_path"]),
        batch_size=int(data.get("batch_size", DEFAULT_BATCH_SIZE)),
        num_workers=int(data.get("num_workers", DEFAULT_NUM_WORKERS)),
        similarity_threshold=float(
            data.get("similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD)
        ),
        max_neighbors=int(data.get("max_neighbors", DEFAULT_MAX_NEIGHBORS)),
        agent_workspace=Path(data.get("agent_workspace")).resolve(),
        agent_model_id=str(data.get("agent_model_id")),
        agent_url=str(data.get("agent_url")),
    )
