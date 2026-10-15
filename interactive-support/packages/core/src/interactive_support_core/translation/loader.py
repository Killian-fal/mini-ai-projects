from functools import cache
from importlib.metadata import entry_points
from importlib.resources import files

from pydantic import TypeAdapter

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.context import Language


type Resource = dict[str, dict[str, str]]

_RESOURCE = TypeAdapter(Resource)


@cache
def translations(language: Language) -> Resource:
    """
    Every `locales/<language>.json` file, merged: an owner (CancelCode, CancelProposal...) lives in a single file.
    Each package with a `locales/` folder declares the package that holds it in its pyproject.toml,
    under [project.entry-points."interactive_support.locales"]: what is installed is read, whatever is imported.
    """
    resource: Resource = {}
    for entry_point in sorted(
        entry_points(group="interactive_support.locales"),
        key=lambda entry_point: entry_point.name,
    ):
        file = files(entry_point.module) / "locales" / f"{language.value.lower()}.json"
        if not file.is_file():
            raise InternalError(
                f"TRANSLATION_FILE_MISSING:{language.value}:{entry_point.name}"
            )

        for owner, texts in _RESOURCE.validate_json(file.read_bytes()).items():
            if owner in resource:
                raise InternalError(f"TRANSLATION_DUPLICATED:{language.value}:{owner}")
            resource[owner] = texts

    return resource
