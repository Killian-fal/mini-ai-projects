from typing import ClassVar

from pydantic import ConfigDict

from interactive_support_flow_api.model.polymorphic import Polymorphic


class Extension(Polymorphic):
    model_config = ConfigDict(frozen=True)

    __key__: ClassVar[str]
