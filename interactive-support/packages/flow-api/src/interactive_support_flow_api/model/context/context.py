from pydantic import BaseModel

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.context import Extension, Issue, Language


class FlowContext(BaseModel):
    issue: Issue
    order_number: str
    language: Language

    extensions: dict[str, Extension] = {}

    def get_extension[T: Extension](self, cls: type[T]) -> T | None:
        extension = self.extensions.get(cls.__key__)
        if extension is None or isinstance(extension, cls):
            return extension
        raise InternalError(f"EXTENSION_KEY_CONFLICT:{cls.__key__}")

    def require_extension[T: Extension](self, cls: type[T]) -> T:
        """
        For an extension an earlier step always sets: its absence is a bug in the flow.
        """
        extension = self.get_extension(cls)
        if extension is None:
            raise InternalError(f"EXTENSION_NOT_FOUND:{cls.__key__}")
        return extension

    def set_extension(self, extension: Extension):
        self.extensions[extension.__key__] = extension

    def has_extension[T: Extension](self, extension: type[T]) -> bool:
        return extension.__key__ in self.extensions
