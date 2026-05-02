from lancedb.pydantic import LanceModel, Vector

EMBEDDING_DIM = 1152


class ImageEntity(LanceModel):
    file_hash: str
    path: str
    vector: Vector(EMBEDDING_DIM)
