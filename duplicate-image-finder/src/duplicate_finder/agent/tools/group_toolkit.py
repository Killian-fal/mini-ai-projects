import shutil
from pathlib import Path

from agno.tools import Toolkit

from duplicate_finder.agent.workspace import resolve_safe_path, unique_filename
from duplicate_finder.repository.duplicate_group.repository import (
    DuplicateGroupRepository,
)
from duplicate_finder.repository.image.repository import ImageRepository


class GroupToolkit(Toolkit):
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
            name="group_toolkit",
            tools=[self.list_groups, self.get_group, self.copy_group],
            instructions=(
                "Use these tools to inspect and copy duplicate groups. "
                "All `dest` paths are RELATIVE to the agent workspace. "
                "Never invent group_ids — always call list_groups first if you don't know one."
            ),
        )

    def list_groups(self) -> str:
        """Lists all detected duplicate image groups with their identifier and number of images.

        :return: One line per group formatted as "<group_id>: <count> images", or a message
            if no duplicate groups have been detected yet.
        """
        rows = self.group_repository.find_all()
        by_group = {}
        for r in rows:
            by_group[r.group_id] = by_group.get(r.group_id, 0) + 1

        if not by_group:
            return "No duplicate groups detected yet."

        return "\n".join(f"{gid}: {count} images" for gid, count in by_group.items())

    def get_group(self, group_id: str) -> str:
        """Returns the list of image paths belonging to a single duplicate group.

        Call `list_groups` first if you do not already know a valid group_id.

        :param group_id: The identifier of the duplicate group, as returned by `list_groups`.
        :return: One line per image formatted as "- <absolute_image_path>", or an error
            message if the group_id is unknown.
        """
        rows = self.group_repository.find_by_group_id(group_id)
        if not rows:
            return f"Unknown group_id: {group_id}"
        return "\n".join(f"- {r.image_path}" for r in rows)

    def copy_group(self, group_id: str, destination: str) -> str:
        """Copies every image of a duplicate group into a destination folder inside the agent workspace.

        The destination folder is created if it does not exist. Filename collisions are
        resolved automatically by appending a suffix.

        :param group_id: The identifier of the duplicate group, as returned by `list_groups`.
        :param destination: Destination folder, RELATIVE to the agent workspace (e.g. "review/group_42").
            Absolute paths or paths escaping the workspace are refused.
        :return: A summary of how many images were copied and where, or an error message.
        """
        rows = self.group_repository.find_by_group_id(group_id)
        if not rows:
            return f"Unknown group_id: {group_id}"

        try:
            target_dir = resolve_safe_path(self.workspace, destination)
        except Exception as e:
            return f"Refused: {e}"
        target_dir.mkdir(parents=True, exist_ok=True)

        copied = 0
        for r in rows:
            src = Path(r.image_path)
            if not src.exists():
                continue

            target = unique_filename(target_dir / src.name)
            try:
                shutil.copy2(src, target)
                copied += 1
            except Exception as e:
                return f"Error copying {src} to {target}: {e}"

        return (
            f"Copied {copied}/{len(rows)} images of group {group_id} to {target_dir}."
        )
