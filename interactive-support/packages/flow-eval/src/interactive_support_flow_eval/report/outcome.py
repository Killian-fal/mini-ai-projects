from pydantic import BaseModel


class Outcome(BaseModel):
    input: str
    expected: str
    group: str
    output: str
    failed_criteria: tuple[str, ...]
    error: str | None
