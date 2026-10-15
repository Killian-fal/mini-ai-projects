from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from interactive_support_flow_api.model.flow import End, StepId
from interactive_support_flow_api.model.message import TextCode
from interactive_support_flow_api.model.question import Location


@dataclass(frozen=True)
class Choice[E: TextCode]:
    """
    The bot asks to pick one of `options`, in this order.
    """

    step: StepId
    options: Sequence[E]

    def __post_init__(self):
        object.__setattr__(
            self, "options", tuple(self.options)
        )  # a list and a tuple of the same options are the same choice


@dataclass(frozen=True)
class Confirm:
    """
    The bot asks to confirm `value`, shown on a map at `location` when there is one.
    """

    step: StepId
    value: str
    location: Location | None = None


@dataclass(frozen=True)
class Text:
    """
    The bot asks for a free text.
    """

    step: StepId


@dataclass(frozen=True)
class Photo:
    """
    The bot asks for a photo.
    """

    step: StepId


@dataclass(frozen=True)
class Form[E: TextCode]:
    """
    The bot asks to fill `fields`, in this order, pre-filled with `values`: the empty fields are left out.
    """

    step: StepId
    fields: Sequence[E]
    values: Mapping[E, str] = field(default_factory=dict[E, str])

    def __post_init__(self):
        object.__setattr__(
            self, "fields", tuple(self.fields)
        )  # a list and a tuple of the same fields are the same form


type Next = Choice[Any] | Confirm | Text | Photo | Form[Any] | End
