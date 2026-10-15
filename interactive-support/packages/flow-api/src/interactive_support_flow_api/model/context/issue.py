from enum import Enum


class Issue(Enum):
    CANCEL = "CANCEL"
    DAMAGED = "DAMAGED"

    # ("CANCEL", "The user wants to cancel his order"),
    # ("LATE", "The user's order is late (the delivery)"),
    # ("NOT_DELIVERED", "The user's order was not delivered"),
