from lancedb.pydantic import LanceModel


class DuplicateGroupEntity(LanceModel):
    group_id: str
    image_path: str
