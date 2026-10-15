from enum import auto

from interactive_support_flow_api.model.message import TextCode


class DamagedCode(TextCode):
    """
    Every message of the DAMAGED flow, translated in `locales/`.
    """

    ORDER_NOT_FOUND = auto()
    ORDER_CANCELLED = auto()
    NOT_DELIVERED_YET = auto()

    ASK_PHOTO = auto()
    NO_DAMAGE_VISIBLE = auto()
    ASK_REPORT_CONFIRMATION = auto()
    ASK_REPORT_CORRECTION = auto()
    SENT_TO_SUPPORT = auto()
