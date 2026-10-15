from abc import abstractmethod, ABC

from pydantic import BaseModel

from interactive_support_flow_api.model.question import Action


class Question[T](ABC, BaseModel):
    @abstractmethod
    def action(self) -> Action:
        pass

    @abstractmethod
    def parse(self, response: str) -> T:
        pass
