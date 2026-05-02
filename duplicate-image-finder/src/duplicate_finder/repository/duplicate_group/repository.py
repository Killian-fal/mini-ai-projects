import uuid

import lancedb

from duplicate_finder.config import Config
from duplicate_finder.repository.duplicate_group.entity import DuplicateGroupEntity
from duplicate_finder.repository.image.entity import ImageEntity

TABLE_NAME = "duplicate_groups"


class DuplicateGroupRepository:
    def __init__(self, config: Config):
        self.config = config
        self.db = lancedb.connect(str(config.db_path))
        self.table = self._ensure_table()

    def _ensure_table(self):
        if TABLE_NAME in self.db.table_names():
            return self.db.open_table(TABLE_NAME)
        return self.db.create_table(TABLE_NAME, schema=DuplicateGroupEntity)

    def save(self, groups: list[list[ImageEntity]]) -> None:
        rows: list[DuplicateGroupEntity] = []
        for group in groups:
            group_id = str(uuid.uuid4())
            for img in group:
                rows.append(
                    DuplicateGroupEntity(group_id=group_id, image_path=img.path)
                )

        self.db.drop_table(TABLE_NAME, ignore_missing=True)
        self.table = self.db.create_table(TABLE_NAME, schema=DuplicateGroupEntity)
        if rows:
            self.table.add(rows)

    def find_all(self) -> list[DuplicateGroupEntity]:
        return [
            DuplicateGroupEntity(**row) for row in self.table.to_arrow().to_pylist()
        ]

    def find_by_image_path(self, image_path: str) -> DuplicateGroupEntity | None:
        escaped = image_path.replace("'", "''")
        results = (
            self.table.search()
            .where(f"image_path = '{escaped}'")
            .limit(1)
            .to_pydantic(DuplicateGroupEntity)
        )
        return results[0] if results else None

    def find_by_group_id(self, group_id: str) -> list[DuplicateGroupEntity]:
        escaped = group_id.replace("'", "''")
        return (
            self.table.search()
            .where(f"group_id = '{escaped}'")
            .to_pydantic(DuplicateGroupEntity)
        )
