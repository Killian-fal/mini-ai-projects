from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    ModelWrapValidatorHandler,
    SerializerFunctionWrapHandler,
    model_serializer,
    model_validator,
)

from interactive_support_flow_api._internal import InternalError

_TYPES: dict[str, type["Polymorphic"]] = {}


class Polymorphic(BaseModel):
    model_config = ConfigDict(polymorphic_serialization=True)

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        if cls.__name__ in _TYPES:
            raise InternalError(f"TYPE_CONFLICT:{cls.__name__}")
        _TYPES[cls.__name__] = cls

    @model_serializer(mode="wrap")
    def _write_type(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        return {"__type__": type(self).__name__, **handler(self)}

    @model_validator(mode="wrap")
    @classmethod
    def _read_type(
        cls, data: Any, handler: ModelWrapValidatorHandler["Polymorphic"]
    ) -> "Polymorphic":
        match data:
            case {"__type__": str() as name} if name != cls.__name__:
                return _TYPES[name].model_validate(data)
            case _:
                return handler(data)
