"""
Reserved to flow-api and core: a flow never imports this module.
A flow raises InvalidAnswer, never InternalError, and calls the LLMs through `llm`, never through the clients.
"""

import dspy
from dspy.clients.typesafe import TypeSafe


class InternalError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# the API keys come from the environment: TYPESAFE_API_KEY and OPENROUTER_API_KEY
JEV_CLIENT = TypeSafe("jev-latest")
GENERATIVE_CLIENT = dspy.LM("openrouter/anthropic/claude-haiku-5.5")

# TODO: rework
