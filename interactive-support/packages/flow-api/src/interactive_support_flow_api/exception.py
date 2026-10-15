from interactive_support_flow_api.model.message import TextCode


class InvalidAnswer(Exception):
    """
    Raised by a step's `run` or a question's `parse` when the user's answer can't be used: the same question is asked again.

    error_code: why the answer can't be used (e.g. CancelCode.ADDRESS_UNREADABLE).
    """

    def __init__(self, error_code: TextCode):
        self.error_code = error_code
        super().__init__(error_code.name)
