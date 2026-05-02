from pathlib import Path


def ensure_workspace(workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=True)


def resolve_safe_path(workspace: Path, rel: str) -> Path:
    workspace_abs = workspace.resolve()
    target = (workspace_abs / rel).resolve()
    if not target.is_relative_to(workspace_abs):
        raise ValueError(f"'{rel}' escapes workspace.")
    return target


def unique_filename(target: Path) -> Path:
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 1
    while True:
        candidate = target.with_name(f"{stem}_{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1
