from interactive_support_flow_api.tools.llm import GenerateInput, GenerateOutput
from interactive_support_flow_test.reply.model import GenerateReply


def generate(given: GenerateInput, output: GenerateOutput) -> GenerateReply:
    """
    One `llm.generate(...)`: it must receive `given` and returns `output`.
    """
    return GenerateReply(given, output)
