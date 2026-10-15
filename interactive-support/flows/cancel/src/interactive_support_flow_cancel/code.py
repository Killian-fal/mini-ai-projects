from enum import auto

from interactive_support_flow_api.model.message import TextCode


class CancelCode(TextCode):
    """
    Every message of the CANCEL flow, translated in `locales/`.
    """

    ORDER_NOT_FOUND = auto()
    ALREADY_CANCELLED = auto()
    TOO_LATE_TO_CANCEL = auto()

    ASK_PROPOSAL = auto()

    ASK_CANCEL_REASON = auto()
    ASK_SERVICE_DETAILS = auto()
    ORDER_CANCELLED = auto()

    ASK_NEW_ADDRESS = auto()
    ADDRESS_UNREADABLE = auto()
    ASK_ADDRESS_DETAILS = auto()
    ADDRESS_NOT_FOUND = auto()
    ASK_ADDRESS_CONFIRMATION = auto()
    ADDRESS_UPDATED = auto()

    ASK_DELIVERY_MODE = auto()
    DELIVERY_MODE_UPDATED = auto()
