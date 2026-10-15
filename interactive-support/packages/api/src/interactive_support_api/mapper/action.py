from interactive_support_api.exception import ApiError
from interactive_support_api.model import (
    ActionDto,
    ActionFormDto,
    ActionPhotoUploadDto,
    ActionTextInputDto,
    ActionUniqueChoiceDto,
    ActionYesNoDto,
    ChoiceDto,
    FormFieldDto,
    LocationDto,
)
from interactive_support_api.translation import t
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.model.question import (
    Action,
    ActionForm,
    ActionPhotoUpload,
    ActionType,
    ActionTextInput,
    ActionUniqueChoice,
    ActionYesNo,
)


class ActionMapper:
    @staticmethod
    def to_dto(action: Action, language: Language) -> ActionDto:
        match action:
            case ActionUniqueChoice():
                return ActionUniqueChoiceDto(
                    type=ActionType.UNIQUE_CHOICE,
                    choices=[
                        ChoiceDto(key=key, label=t(language, key))
                        for key in action.choices
                    ],
                )
            case ActionTextInput():
                return ActionTextInputDto(type=ActionType.TEXT_INPUT)
            case ActionYesNo():
                return ActionYesNoDto(
                    type=ActionType.YES_NO,
                    value=action.value,
                    location=(
                        None
                        if action.location is None
                        else LocationDto(
                            latitude=action.location.latitude,
                            longitude=action.location.longitude,
                        )
                    ),
                )
            case ActionPhotoUpload():
                return ActionPhotoUploadDto(type=ActionType.PHOTO_UPLOAD)
            case ActionForm():
                return ActionFormDto(
                    type=ActionType.FORM,
                    fields=[
                        FormFieldDto(key=key, label=t(language, key), value=value)
                        for key, value in action.fields.items()
                    ],
                )
            case _:
                raise ApiError(f"ACTION_UNKNOWN:{type(action).__name__}")
