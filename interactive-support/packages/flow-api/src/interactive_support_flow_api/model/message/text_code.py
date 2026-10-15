from enum import Enum


class TextCode(Enum):
    """
    Empty base of every text shown to the user: each owner (a flow, the opening, a question...) extends it with its codes,
    and translates them in the `locales/<language>.json` files next to it.
    """

    @property
    def key(self) -> str:
        return f"{type(self).__name__}.{self.name}"
