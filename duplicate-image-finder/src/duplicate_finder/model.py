from dataclasses import dataclass


@dataclass(frozen=True)
class ImageToProcess:
    file_hash: str
    path: str
