from enum import Enum
from typing import cast

from interactive_support_flow_api.model.flow import End
from interactive_support_flow_test.model import Choice, Confirm, Form, Photo, Text


def show(value: object) -> str:
    """
    A value as the test writes it, for the failure messages.
    """
    match value:
        case End():
            return "END"
        case Enum():
            return f"{type(value).__name__}.{value.name}"
        case Choice():
            return f"Choice({show(value.step)}, {show(list(value.options))})"
        case Confirm():
            return f"Confirm({show(value.step)}, {value.value!r})"
        case Text():
            return f"Text({show(value.step)})"
        case Photo():
            return f"Photo({show(value.step)})"
        case Form():
            return f"Form({show(value.step)}, {show(list(value.fields))}, {show(dict(value.values))})"
        case dict():
            items = cast(dict[object, object], value).items()
            return "{" + ", ".join(f"{show(k)}: {show(v)}" for k, v in items) + "}"
        case list():
            return (
                "[" + ", ".join(show(item) for item in cast(list[object], value)) + "]"
            )
        case _:
            return repr(value)
