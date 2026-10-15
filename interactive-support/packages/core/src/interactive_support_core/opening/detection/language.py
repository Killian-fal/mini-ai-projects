from enum import Enum

from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.tools import llm

LANGUAGE_QUESTION = "In which language is the customer message written?"


class LanguageDetection(Enum):
    FR = "When the input message is in French"
    EN = "When the input message is in English"
    OTHER = "Other"


def to_language(result: llm.ChoiceResult[LanguageDetection]) -> Language:
    if result.confidence < 0.5 or result.value is LanguageDetection.OTHER:
        return Language.EN  # TODO : ASk avec LLM

    return Language[result.value.name]
