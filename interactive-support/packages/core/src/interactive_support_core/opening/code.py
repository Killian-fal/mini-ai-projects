from enum import auto

from interactive_support_flow_api.model.context import Issue
from interactive_support_flow_api.model.message import TextCode


class OpeningCode(TextCode):
    ASK_ISSUE = auto()
    ASK_ISSUE_CHOICE = auto()
    VALID_ISSUE = auto()
    ASK_ORDER_NUMBER = auto()
    ORDER_NUMBER_UNREADABLE = auto()
    VALID_ORDER_NUMBER = auto()
    COMPLETE_CONVERSATION = auto()


class IssueChoice(TextCode):
    CANCEL = Issue.CANCEL
    DAMAGED = Issue.DAMAGED
    OTHER = None
