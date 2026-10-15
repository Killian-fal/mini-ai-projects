import base64
import binascii
from enum import auto
from urllib.parse import urlparse

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.question import (
    Question,
    Action,
    ActionPhotoUpload,
)
from interactive_support_flow_api.model.message import TextCode


class PhotoCode(TextCode):
    NOT_A_PHOTO = auto()
    URL_NOT_ACCEPTED = auto()


class PhotoQuestion(Question[str]):
    def action(self) -> Action:
        return ActionPhotoUpload()

    def parse(self, response: str) -> str:
        if urlparse(response).scheme in ("http", "https"):
            raise InvalidAnswer(PhotoCode.URL_NOT_ACCEPTED)

        header, _, payload = response.partition(",")
        if header.startswith("data:image/") and header.endswith(";base64") and payload:
            try:
                base64.b64decode(payload, validate=True)
                return response
            except binascii.Error:
                pass
        raise InvalidAnswer(PhotoCode.NOT_A_PHOTO)
