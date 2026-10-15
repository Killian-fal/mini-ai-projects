import dspy
from dspy.utils.exceptions import AdapterParseError
from pydantic import ValidationError
from pydantic.fields import FieldInfo

from interactive_support_flow_api._internal import InternalError, GENERATIVE_CLIENT
from interactive_support_flow_api.tools.llm.model import GenerateInput, GenerateOutput


def generate[O: GenerateOutput](
    instruction: str, generate_input: GenerateInput, generate_output: type[O]
) -> O:
    """
    Single call to a generative LLM: it reads the fields of `generate_input` and produces an instance of `generate_output`.

    instruction: what the LLM must do, e.g. "Extract the new delivery address written by the customer."
    """
    if type(generate_input).model_fields.keys() & generate_output.model_fields.keys():
        raise InternalError("LLM_FIELD_CONFLICT")

    return _call(instruction, generate_input, generate_output)


def _call[O: GenerateOutput](
    instruction: str, generate_input: GenerateInput, generate_output: type[O]
) -> O:
    inputs = type(generate_input).model_fields
    outputs = generate_output.model_fields

    input_fields: dict[str, tuple[type, FieldInfo]] = {
        name: (field.annotation, dspy.InputField(desc=field.description or ""))
        for name, field in inputs.items()
        if field.annotation is not None
    }
    output_fields: dict[str, tuple[type, FieldInfo]] = {
        name: (field.annotation, dspy.OutputField(desc=field.description or ""))
        for name, field in outputs.items()
        if field.annotation is not None
    }
    fields = input_fields | output_fields

    predict = dspy.Predict(dspy.make_signature(fields, instruction))
    predict.set_lm(GENERATIVE_CLIENT)
    try:
        with dspy.context(adapter=dspy.JSONAdapter()):
            prediction = predict(**dict(generate_input))
        return generate_output.model_validate(
            {name: prediction[name] for name in outputs}
        )
    except (AdapterParseError, ValidationError) as e:
        raise InternalError("LLM_INVALID_OUTPUT") from e
