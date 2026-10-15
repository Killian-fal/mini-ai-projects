from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.model.message import TextCode
from interactive_support_core.translation.loader import translations


def check_translations():
    owners = (
        TextCode.__subclasses__()
    )  # an enum with members can't be extended: the direct subclasses are all the codes
    names = [owner.__name__ for owner in owners]
    if duplicated := sorted({name for name in names if names.count(name) > 1}):
        raise InternalError(f"TEXT_CODE_DUPLICATED:{','.join(duplicated)}")

    expected = {code.key for owner in owners for code in owner}
    for language in Language:
        found = {
            f"{owner}.{name}"
            for owner, texts in translations(language).items()
            for name in texts
        }
        if missing := sorted(expected - found):
            raise InternalError(
                f"TRANSLATION_MISSING:{language.value}:{','.join(missing)}"
            )
        if unknown := sorted(found - expected):
            raise InternalError(
                f"TRANSLATION_UNKNOWN:{language.value}:{','.join(unknown)}"
            )
