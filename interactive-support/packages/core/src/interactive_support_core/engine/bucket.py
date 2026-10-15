from interactive_support_flow_api.model.message import Bucket, GeneratedText, TextCode
from interactive_support_core.model import (
    Message,
    MessageCode,
    MessageRole,
    MessageText,
)


class MessageBucket(Bucket):
    def __init__(self):
        self.messages: list[Message] = []

    def add_code(self, code: TextCode):
        self.messages.append(MessageCode(role=MessageRole.ASSISTANT, code=code.key))

    def add_generated(self, text: GeneratedText):
        self.messages.append(
            MessageText(role=MessageRole.ASSISTANT_GEN, text=text.text)
        )
