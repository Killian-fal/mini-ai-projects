import lancedb

from duplicate_finder.config import Config
from duplicate_finder.repository.image.entity import ImageEntity

TABLE_NAME = "images"


class ImageRepository:
    def __init__(self, config: Config):
        self.config = config
        self.db = lancedb.connect(str(config.db_path))
        self.table = self._ensure_table()

    def _ensure_table(self):
        if TABLE_NAME in self.db.table_names():
            return self.db.open_table(TABLE_NAME)
        return self.db.create_table(TABLE_NAME, schema=ImageEntity)

    def find_by_file_hash(self, file_hash: str) -> ImageEntity | None:
        escaped = file_hash.replace("'", "''")
        results = (
            self.table.search()
            .where(f"file_hash = '{escaped}'")
            .limit(1)
            .to_pydantic(ImageEntity)
        )
        return results[0] if results else None

    def find_by_path(self, path: str) -> ImageEntity | None:
        escaped = path.replace("'", "''")
        results = (
            self.table.search()
            .where(f"path = '{escaped}'")
            .limit(1)
            .to_pydantic(ImageEntity)
        )
        return results[0] if results else None

    def find_all(self) -> list[ImageEntity]:
        return [ImageEntity(**row) for row in self.table.to_arrow().to_pylist()]

    def find_similar(
        self,
        path: str,
        vector: list[float],
        threshold: float,
        limit: int,
    ) -> list[ImageEntity]:
        escaped = path.replace("'", "''")
        rows = (
            self.table.search(vector)
            .distance_type("cosine")
            .where(f"path != '{escaped}'")
            .limit(limit)
            .to_list()
        )
        return [ImageEntity(**row) for row in rows if row["_distance"] <= threshold]

    def insert(self, image: ImageEntity) -> None:
        self.table.add([image])

    def find_orphans(
        self, grouped_paths: set[str], limit: int, offset: int
    ) -> tuple[list[str], int]:
        rows = self.table.search().select(["path"]).to_list()
        orphans = sorted(r["path"] for r in rows if r["path"] not in grouped_paths)
        return orphans[offset : (offset + limit)], len(orphans)
