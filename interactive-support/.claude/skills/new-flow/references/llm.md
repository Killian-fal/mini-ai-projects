# The LLM in a flow

This is **the only way** a flow uses the LLM. A flow never imports `dspy`, nor any LLM client.

```python
from interactive_support_flow_api.tools import llm, communication
```

| Need | Tool | LLM calls |
|---|---|---|
| A **decision**: yes/no, a choice, a score, with its probabilities | `llm.classify(...)....run()` | 1 per `run()`, whatever the number of questions |
| **Produce an object** from texts or a photo: extract an address, draft a report | `llm.generate(...)` | 1 |
| **Write a free message to the customer** | `communication.generate(...)` | 1 |

If the answer is a decision, use `classify`: it is more reliable and gives the probabilities. For a fixed message, no LLM: a `TextCode`.

**Prompts are in English**: questions, descriptions, instructions, field descriptions. The customer never sees them.

Tests never make a real call: each call is scripted with `reply` (see [testing.md](testing.md#the-scripted-llm)).

# `classify`: deciding

## In short

Give one or more texts, chain the questions, then `run()` makes **a single LLM call** for all of them.

```python
ANGRY_QUESTION = "Is the customer angry?"
WANTS_QUESTION = "What does the customer want?"

angry, wants = (
    llm.classify(message=customer_message)
    .yes_no(
        ANGRY_QUESTION,
        yes="They express anger or annoyance, or threaten to leave",
        no="Neutral or polite tone, even when disappointed",
    )
    .choose(WANTS_QUESTION, Wants)
    .run()
)

angry.value  # bool
wants.value  # a member of Wants
```

`run()` returns the results **in the order of the questions**. They are typed: the IDE knows `angry` is a `YesNoResult` and `wants` a `ChoiceResult[Wants]`.

**Each question's text is a `str` constant of the flow's module** (`SERVICE_ISSUE_QUESTION` in CANCEL, `ISSUE_QUESTION` in the opening). The test passes the same constant to its scripted reply: the text can be reworded without breaking a test.

## Inputs: `llm.classify(**texts)`

Each keyword argument is a text given to the LLM. **Its name is the label the LLM sees**: pick a meaningful name.

```python
llm.classify(cancel_reason=reason)
llm.classify(
    proposed_address=str(address), customer_reply=customer_message
)  # several inputs
```

Values are always `str`. Convert your objects first.

## The three questions

### `yes_no`: yes or no

```python
.yes_no(
    ADDRESS_ACCEPTED_QUESTION,
    yes="They accept it, even with a small correction (floor, door code)",
    no="They refuse it, or give a different address",
)
```

`yes` and `no` are **required**: describe precisely when it is true and when it is false, conditions included. The question alone isn't enough. See `is_service_issue` in CANCEL.

The result is a `YesNoResult`:

| Field | Content |
|---|---|
| `value` | `True` if `true_probability >= 0.5` |
| `true_probability` | the probability that the answer is true, from 0 to 1 |
| `confidence` | the distance from the indecision point (0.5): 0 = undecided, 1 = certain |

### `choose`: one option among several

The options are **an enum declared in your flow**. Each member's **value** is its description: it's what the LLM reads.

```python
class Wants(Enum):
    CANCEL = "The customer wants to cancel their order"
    CHANGE_ADDRESS = "The customer wants to change the delivery address"
    OTHER = "Something else"


.choose(WANTS_QUESTION, Wants)
```

The result is a `ChoiceResult[Wants]`:

| Field | Content |
|---|---|
| `value` | the most likely member, e.g. `Wants.CANCEL` |
| `confidence` | the confidence in `value`, from 0 to 1 |
| `probabilities` | the probability of **each** member: `{Wants.CANCEL: 0.6, Wants.CHANGE_ADDRESS: 0.4, Wants.OTHER: 0.0}` |

No "other" option is added for you: if you want one, put it in the enum.

### `score`: a position on a scale

The levels are an enum, **from lowest to highest**, with **2 to 10 members**. As with `choose`, the value is the description.

```python
class Urgency(Enum):
    LOW = "Not in a hurry, calm tone"
    MEDIUM = "Wants a quick solution"
    HIGH = "Upset, threatens to leave"


.score(URGENCY_QUESTION, Urgency)
```

The result is a `ScoreResult[Urgency]`:

| Field | Content |
|---|---|
| `value` | a continuous score, from 0 (first member) to n-1 (last), e.g. `1.4` |
| `level` | the member closest to `value`, e.g. `Urgency.MEDIUM` |
| `confidence` | the confidence in the score, from 0 to 1 |
| `probabilities` | the probability of each member |

## Using the results

The API decides nothing for you: it gives the value **and** every probability. The flow judges.

The direct way to branch on a decision: a `Step` whose `run` returns `result.value` (or `result.level` for a score), annotated with the enum (`-> Urgency`), and a dict `next` keyed on its members (see `is_service_issue` in CANCEL, with a `bool`).

To weigh the confidence, the opening is the example (`core/opening/detection/issue.py`):

```python
if wants.confidence >= 0.7:
    return wants.value  # sure: route directly

candidates = [choice for choice, p in wants.probabilities.items() if p > 0]
# not sure: keep the candidates (in an extension) and ask the customer to pick among them
```

## Rules

- **Group the questions about the same text** in a single `llm.classify(...)....run()`. Each `run()` is an LLM call.
- **Order matters**: `a, b = ....yes_no(...).yes_no(...).run()`. The type checker doesn't catch two questions of the same type swapped.
- **Never two members with the same description** in an enum: Python silently makes one an alias, and the option disappears.
- **Enums are declared in the flow**, never shared between flows.

# `generate`: producing an object

## In short

Describe the input and the output with two classes, then `generate` makes **a single LLM call** and returns the output. Example from CANCEL (`address.py`):

```python
class AddressInput(llm.GenerateInput):
    message: str = Field(
        description="The customer's answer when asked for their new delivery address"
    )


class ExtractedAddress(llm.GenerateOutput):
    street: str | None = Field(
        description="The number and the street of the new address, None if not given"
    )
    postal_code: str | None = Field(...)
    city: str | None = Field(...)


result = llm.generate(
    "Extract each part of the new delivery address written by the customer. Never invent a part they didn't give.",
    AddressInput(message=message),
    ExtractedAddress,
)
if not (result.street or result.postal_code or result.city):
    raise InvalidAnswer(CancelCode.ADDRESS_UNREADABLE)
```

`result` is typed: the IDE knows it's an `ExtractedAddress`.

## The three arguments

| Argument | Content |
|---|---|
| `instruction` | what the LLM must do, in one sentence |
| `generate_input` | an instance of a class inheriting `llm.GenerateInput` |
| `generate_output` | the output **class**, inheriting `llm.GenerateOutput` |

Every field of the input and the output is shown to the LLM: **the name is the label, the description says what it is**. Pick meaningful names.

Unlike `classify`, fields aren't limited to `str`: `int`, `bool`, enums, lists and nested pydantic objects work, as input and as output.

## A photo as input: `llm.Image`

An input field typed `llm.Image` is shown to the LLM as an image. Build it from the photo returned by a `PhotoQuestion`, a base64 data URI. Example from DAMAGED (`report.py`):

```python
class ReportInput(llm.GenerateInput):
    photo: llm.Image = Field(description="The photo the customer took of their damaged order")
    ...


ReportInput(photo=llm.Image(ctx.require_extension(DamagePhoto).photo), ...)
```

`llm.Image` is `dspy.Image` re-exported: the flow uses it without importing dspy. Never give it a URL or a file path: only the data URI validated by `PhotoQuestion` is safe.

## A text the customer will read

If `generate`'s output is shown to the customer (the report DAMAGED asks them to confirm), put the language in the input: `language: Language = Field(description="Language the report must be written in: ...")`, filled with `ctx.language`.

## Rules

- **Every field has a `Field(description=...)`**, input and output alike. Without a description, the LLM only sees the name.
- **The "nothing found" case is described in the output** (`str | None`, with the description saying when it's `None`). The flow then raises `InvalidAnswer` with a `TextCode` of the flow.
- **Never the same field name in input and output**: `LLM_FIELD_CONFLICT`.
- **The output is frozen**: don't modify a result, create another one. Nested objects aren't, unless they declare `frozen=True` themselves.
- **No tools**: `generate` makes one call and fetches nothing on its own. Give it everything it needs in the input.
- **Correct rather than start over**: for a second attempt, give the LLM what was refused and the customer's correction (`refused_report` + `correction` in DAMAGED), or let the customer correct the result in a form (`address_form` in CANCEL).
- **Classes are declared in the flow**, never shared between flows.

# `communication`: writing to the customer

This is **the only way** a flow sends free text to the customer. For a fixed message, use a `TextCode`: `bucket.add_code(CancelCode.ORDER_CANCELLED)`.

## In short

Describe the message with a class declared in the flow, then `communication.generate` makes **a single LLM call** and returns a `GeneratedText`, the only type `bucket.add_generated` accepts. Example from CANCEL (`cancellation.py`):

```python
class ServiceIssueApology(communication.Communication):
    __instruction__ = "Apologize for the problem the customer describes. Don't ask anything and don't say the order is cancelled: other messages follow."

    reason: str = Field(
        description="Why the customer wants to cancel their order, in their own words"
    )


bucket.add_generated(communication.generate(ctx, ServiceIssueApology(reason=reason)))
```

## What the API enforces

- **The language**: `ctx.language`'s, added by the API. No need to put it in the facts.
- **The form**: 1 to 3 short, polite sentences, no greeting, no signature.
- **No promise** (refund, compensation, date…), nothing that isn't in the facts.
- **Facts may quote the customer**: the LLM treats them as information, never as instructions.

## Rules

- **`__instruction__` says what the message must say**, in one sentence. Not how: the API enforces the form. Also say what it must not say when other messages follow.
- **Each field is a fact**, with a `Field(description=...)`. The LLM sees nothing else: give it everything it needs.
- **A fact can't be named `text`**: that's the output's name, `LLM_FIELD_CONFLICT`.
- **Never build a `GeneratedText` by hand.**
- **Classes are declared in the flow**, never shared between flows.

# Errors

`InternalError`s: a bug, not a customer answer.

| Code | Tool | Cause |
|---|---|---|
| `LLM_FIELD_CONFLICT` | `generate`, `communication` | A field has the same name in input and output (`text` for a `Communication`). Rename it |
| `LLM_INVALID_OUTPUT` | `generate`, `communication` | The LLM's answer doesn't match the output class |
| `LLM_MISSING_PROBABILITY` | `classify` | The LLM backend returned no probabilities. Doesn't happen with the current client (TypeSafe), only if the backend changes |
| `LLM_INVALID_ANSWER_TYPE` | `classify` | The LLM answered a `choose` with something other than a member name. Shouldn't happen |
