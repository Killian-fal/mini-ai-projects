from typing import Annotated, Literal

from pydantic import BaseModel, Field

from interactive_support_flow_api.model.question import ActionType


class ChoiceDto(BaseModel):
    key: str
    label: str


class ActionUniqueChoiceDto(BaseModel):
    type: Literal[ActionType.UNIQUE_CHOICE]
    choices: list[ChoiceDto]


class ActionTextInputDto(BaseModel):
    type: Literal[ActionType.TEXT_INPUT]


class LocationDto(BaseModel):
    latitude: float
    longitude: float


class ActionYesNoDto(BaseModel):
    type: Literal[ActionType.YES_NO]
    value: str
    location: LocationDto | None


class ActionPhotoUploadDto(BaseModel):
    type: Literal[ActionType.PHOTO_UPLOAD]


class FormFieldDto(BaseModel):
    key: str
    label: str
    value: str


class ActionFormDto(BaseModel):
    type: Literal[ActionType.FORM]
    fields: list[FormFieldDto]


ActionDto = Annotated[
    ActionUniqueChoiceDto
    | ActionTextInputDto
    | ActionYesNoDto
    | ActionPhotoUploadDto
    | ActionFormDto,
    Field(discriminator="type"),
]
