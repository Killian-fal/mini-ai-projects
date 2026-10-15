from interactive_support_core.opening.code import IssueChoice
from interactive_support_core.opening.detection.issue import (
    ISSUE_QUESTION,
    IssueDetection,
    to_issue_candidates,
)
from interactive_support_core.opening.detection.language import (
    LANGUAGE_QUESTION,
    LanguageDetection,
    to_language,
)
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.tools import llm


def detect_first_message(message: str) -> tuple[Language, list[IssueChoice]]:
    language, issue = (
        llm.classify(customer_message=message)
        .choose(LANGUAGE_QUESTION, LanguageDetection)
        .choose(ISSUE_QUESTION, IssueDetection)
        .run()
    )
    return to_language(language), to_issue_candidates(issue)


def detect_issue(message: str) -> list[IssueChoice]:
    (issue,) = (
        llm.classify(customer_message=message)
        .choose(ISSUE_QUESTION, IssueDetection)
        .run()
    )
    return to_issue_candidates(issue)
