import shutil
from pathlib import Path

from agno.tools import Toolkit

from duplicate_finder.agent.workspace import resolve_safe_path, unique_filename
from duplicate_finder.repository.duplicate_group.repository import (
    DuplicateGroupRepository,
)
from duplicate_finder.repository.image.repository import ImageRepository


class ImageToolkit(Toolkit):
    def __init__(
        self,
        image_repository: ImageRepository,
        group_repository: DuplicateGroupRepository,
        workspace: Path,
    ):
        self.image_repository = image_repository
        self.group_repository = group_repository
        self.workspace = workspace
        super().__init__(
            name="image_toolkit",
            tools=[self.list_orphan_images, self.copy_image],
            instructions=(
                "Use these tools for individual images. "
                "Orphan images are images that do NOT belong to any duplicate group. "
                "list_orphan_images is paginated — call it again with offset += limit if you need more."
            ),
        )

    def list_orphan_images(self, limit: int = 50, offset: int = 0) -> str:
        """List images that are NOT part of any duplicate group, paginated."""
        limit = max(1, min(limit, 200))
        offset = max(0, offset)

        # berk
        grouped = [r.image_path for r in self.group_repository.find_all()]
        page, total = self.image_repository.find_orphans(grouped, limit, offset)

        if total == 0:
            return "total_orphans=0"
        return "\n".join(page) + f"\ntotal_orphans={total}"

    def copy_image(self, image_path: str, dest: str) -> str:
        """Copy a single image into a destination folder under the workspace.
        => image_path: Absolute path of the source image (use list_orphan_images to find one).
        => dest: Destination folder, RELATIVE to the agent workspace. Created if missing.
        """
        src = Path(image_path)
        if not src.exists():
            return f"Source not found: {image_path}"

        try:
            target_dir = resolve_safe_path(self.workspace, dest)
        except Exception as e:
            return f"Refused: {e}"
        target_dir.mkdir(parents=True, exist_ok=True)

        target = unique_filename(target_dir / src.name)
        try:
            shutil.copy2(src, target)
            return f"Copied {src} to {target}."
        except Exception as e:
            return f"Error copying {src} to {target}: {e}"
