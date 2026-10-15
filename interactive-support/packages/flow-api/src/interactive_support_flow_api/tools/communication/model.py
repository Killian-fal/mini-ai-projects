from typing import ClassVar

from interactive_support_flow_api.tools.llm import GenerateInput


class Communication(GenerateInput):
    """
    Base of a message the LLM writes to the user, declared in the flow.

    __instruction__: what the message must say.
    Each field is a fact the LLM may use, described with `Field(description=...)`.
    The language comes from ctx.language: no need to add it as a field.
    """

    __instruction__: ClassVar[str]
