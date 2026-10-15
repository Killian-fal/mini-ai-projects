from pydantic import BaseModel


class Case[Input, Expected](BaseModel):
    input: Input
    expected: Expected
    group: str
