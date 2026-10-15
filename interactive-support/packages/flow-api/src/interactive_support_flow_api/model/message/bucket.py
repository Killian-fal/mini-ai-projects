from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from interactive_support_flow_api.model.message import TextCode


class GeneratedText(BaseModel):
    """
    Text written for the user by `communication.generate`. Never built by hand.
    """

    model_config = ConfigDict(frozen=True)

    text: str


class Bucket(ABC):
    @abstractmethod
    def add_code(self, code: TextCode):
        pass

    @abstractmethod
    def add_generated(self, text: GeneratedText):
        pass
