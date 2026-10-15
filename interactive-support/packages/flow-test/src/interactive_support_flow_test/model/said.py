from interactive_support_flow_api.model.message import TextCode
from interactive_support_flow_api.tools.communication import Communication

type Said = (
    TextCode | Communication
)  # a fixed message, or the Communication the LLM wrote
