from interactive_support_core.translation import translations
from interactive_support_flow_api.model.context import Language


def t(language: Language, key: str) -> str:
    owner, _, name = key.partition(".")
    return translations(language)[owner][name]


def t_or_none(language: Language, key: str) -> str | None:
    owner, _, name = key.partition(".")
    return translations(language).get(owner, {}).get(name)
