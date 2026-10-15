# Writing a flow

How steps are written, and why. The reference is `flows/cancel/src/interactive_support_flow_cancel/`.

## The `Flow`

```python
CANCEL_FLOW = Flow(
    issue=Issue.CANCEL,
    description="The user wants to cancel his order",
    steps=[...],
)
```

- **`issue`**: the problem the flow handles. One flow per `Issue`.
- **`description`**: one sentence, in English, read by the opening's LLM to recognize the problem. It must tell this problem apart from the others. The customer never sees it.
- **`steps`**: **the first one is the flow's entry**. The order of the others doesn't matter, only `next` decides.

## `Step` and `AskStep`

| | `Step`: acts without asking | `AskStep[T]`: asks a question |
|---|---|---|
| `id` | a member of the flow's `StepId` | same |
| `pre_hook(ctx, bucket)` | optional, before `run` | optional, before the question: shows the `ASK_*` |
| `question(ctx) -> Question[T]` | — | the question asked |
| `run` | `run(ctx, bucket) -> value` | `run(ctx, answer: T, bucket) -> value`, defaults to `forward`, which returns the answer |
| `next` | where to go next | same |

**A turn, seen from the flow:**

1. The engine reaches a step and calls its `pre_hook`.
2. A `Step` runs `run`, then moves to the next step **in the same turn**. An `AskStep` publishes its question and the turn stops.
3. When the customer answers, the engine **calls `question(ctx)` again** to read the answer (`parse`), then calls the `AskStep`'s `run` with the parsed answer, and continues with `next`.

`question(ctx)` is thus called several times: when asking, when reading the answer, and by flow-test. **It must rebuild identically from `ctx`** (and the domain): no randomness, no state kept elsewhere.

## `next`

| Form | When |
|---|---|
| `next=CancelStep.IS_SERVICE_ISSUE` | always the same step |
| `next=END` | the flow ends |
| `next={True: CancelStep.APOLOGIZE, False: CancelStep.CANCEL_ORDER}` | depending on the value returned by `run`: each key is a possible value |

With a dict `next`:
- **`run` is a real, annotated function** stating what it returns: `-> bool`, `-> MyEnum`, `-> OrderStatus | None`. Never a lambda. Every possible value needs its key, and no extra key: `check_flow` raises `FLOW_NEXT_UNTYPED` or `FLOW_NEXT_NOT_EXHAUSTIVE`.
- **With `forward`** (an `AskStep` without `run`), the key is the answer itself: an option of the `ChoiceQuestion`, or `True`/`False` for a `ConfirmationQuestion`. Every offered option needs its key: flow-test checks it when the question is asked (`NEXT_MISSING_OPTION`).

A loop is allowed if it goes through an `AskStep` (DAMAGED asks for a correction until the report is confirmed). A loop of plain `Step`s would run forever: `FLOW_LOOP_WITHOUT_ASK`.

## Questions

| Question | The customer sees | `run` receives | Rejected answer |
|---|---|---|---|
| `TextQuestion()` | a text field | `str` | never |
| `ChoiceQuestion(options=[...])` | the options' translations, in this order | the chosen option, a member of the `TextCode` | `ChoiceCode.UNKNOWN_CHOICE` |
| `ConfirmationQuestion(value=..., location=...)` | `value`, to confirm, on a map when `location` is given (CANCEL's `address_confirmation`) | `bool` | `ConfirmationCode.NOT_A_BOOLEAN` |
| `PhotoQuestion()` | a photo upload | `str`: the base64 data URI (`data:image/...;base64,...`) | `PhotoCode.URL_NOT_ACCEPTED` for a URL, `PhotoCode.NOT_A_PHOTO` for anything else |
| `FormQuestion(fields=[...], values={...})` | a form: the fields' translations as labels, in this order, pre-filled with `values` | `dict` field → value, every field filled | `FormCode.MISSING_FIELD` for an empty field, `FormCode.NOT_A_FORM` for anything else |

- **The options of a choice and the fields of a form are `TextCode`s**: the front shows their translation and sends back their key.
- **Every field of a form is required.** `values` pre-fills it, from an extension: a missing or `None` field is shown empty.
- **A URL is never accepted as a photo**: the LLM or the server would fetch it. `PhotoQuestion` is the guard, don't bypass it.
- **A dynamic question** is a function of `ctx`: `delivery_mode_choice` offers every mode but the current one, `address_form` pre-fills the form with the address the LLM read, kept in an extension.

## `InvalidAnswer`: asking again

```python
if result.address is None:
    raise InvalidAnswer(CancelCode.ADDRESS_UNREADABLE)
```

Raised in an `AskStep`'s `run`, or in a `parse`, it means "this answer can't be used":
- the customer gets the code's message;
- **everything the turn did is undone**: the engine works on a copy of the context, and the turn's messages are dropped;
- the same question is asked again, **without its `pre_hook`** (the `ASK_*` isn't repeated).

That's its only use. In a `Step`, there is no question to ask again: the exception would surface as a bug.

A bug of the flow itself is not an `InvalidAnswer`, and a flow never raises `InternalError` (it lives in `_internal`). Its bugs surface on their own, through `require_extension` (`EXTENSION_NOT_FOUND`) or the domain's `OrderError`, and nothing catches them.

## Context and extensions

`FlowContext` holds `issue`, `order_number`, `language` and the `extensions`: what the flow remembers from one step to the next. It is **the only place** a flow keeps anything, because the context lives in the `Conversation`.

```python
class NewAddress(Extension):
    __key__ = "new_address"

    address: str
```

- An extension is frozen and JSON-serializable. Its fields are simple types, enums or pydantic models. No live object, no function.
- **`__key__`** is unique within the flow. **The class name** is unique across the whole project, otherwise `TYPE_CONFLICT` at import.
- `ctx.set_extension(NewAddress(address=...))` stores or replaces the extension.
- `ctx.require_extension(NewAddress)` is for when an earlier step always set it: its absence is a bug (`EXTENSION_NOT_FOUND`).
- `ctx.get_extension(NewAddress)` returns `None` when absence is normal. Say why in a comment: `# only set when the customer refused the previous one`.
- `ctx.has_extension(NewAddress)` tests presence.

## Messages to the customer

The `bucket` passed to `pre_hook` and `run` collects the turn's messages:
- `bucket.add_code(CancelCode.ORDER_CANCELLED)` for a fixed message;
- `bucket.add_generated(communication.generate(ctx, ...))` for a text written by the LLM (see [llm.md](llm.md)).

## `TextCode`s and translations

Every text shown to the customer is a member of a `TextCode`. Its key, `CancelCode.ASK_PROPOSAL`, is what the back stores, and translates for the front.

```python
class CancelCode(TextCode):  # code.py: every message of the flow
    ORDER_NOT_FOUND = auto()
    ASK_PROPOSAL = auto()
    ...


class CancelProposal(TextCode):  # flow.py: the options of a choice
    CANCEL = auto()
    CHANGE_ADDRESS = auto()
```

- **Each class name is unique across the project**: prefix it with the flow's name (`CancelCode`, `CancelProposal`, `DamagedCode`). Otherwise `TEXT_CODE_DUPLICATED`.
- **A `TextCode` inherits directly from `TextCode`**: an enum that has members can't be extended.
- **Showing a domain enum**: don't change it, declare a `TextCode` whose values are its members. The chosen option gives the domain member through `.value`:

  ```python
  class CancelDeliveryModeChoice(TextCode):
      HOME = orders.DeliveryMode.HOME
      RELAY_POINT = orders.DeliveryMode.RELAY_POINT
      STORE = orders.DeliveryMode.STORE
  ```

- **Every code is translated in every `Language`** (EN, FR), in the `locales/<language>.json` files of the package that declares it. The JSON is keyed by class, then by member:

  ```json
  {
    "CancelCode": { "ASK_PROPOSAL": "Que souhaitez-vous faire ?" },
    "CancelProposal": { "CANCEL": "Annuler la commande" }
  }
  ```

- Tone: formal "vous" in French, short sentences, no promise. Copy the existing files.

## CANCEL's conventions

They are in `flow.py`'s docstring, and an agent copying CANCEL must find them again.

- **`flow.py`'s docstring** says what the flow does, in two or three sentences, and restates the naming rule.
- **The first step is `ORDER_STATUS`**: `order_status(ctx, bucket) -> OrderStatus | None`, with a key for every status and `None → ORDER_NOT_FOUND`, since the opening only checks the number's format. Statuses with nothing to do get their message and go to `END`.
- **The domain is read again when needed**, never copied into an extension: `delivery_mode_choice` calls `orders.get`. To branch on the status later in the flow, add a `Step` that reads it again and returns a `bool` (`is_shipped`).
- **Naming**: an `AskStep` is named after what it asks and its `pre_hook` shows `ASK_<id>` (`NEW_ADDRESS` → `CancelCode.ASK_NEW_ADDRESS`). A `Step` is named after its `run` (`CANCEL_ORDER` → `cancel_order`).
- **Steps that act never ask a question.** The `AskStep`s before them only save the answer in an extension (`save_cancel_reason`). The action (`cancel_order`, `update_address`) is a separate `Step`, which reads the extensions.
- **A message alone** is written as a lambda: `run=lambda ctx, bucket: bucket.add_code(CancelCode.ALREADY_CANCELLED), next=END`. Same for a `pre_hook` or a question without logic. Everything else is a named function.
- **Step functions are grouped by theme**, one function per step: `address.py`, `cancellation.py`, `delivery.py`, `status.py`. Each module also declares its theme's extensions, LLM inputs and outputs, and question constants.
- **The list of steps is split into sections**: `# --- Cancel: a service issue gets an apology and a request for details first`.
- **Nothing is shared between flows**: enums, extensions, `Communication`, `GenerateInput`, even `status.py`, which is copied. Each flow stands alone.
- **The code and its comments are in English**, like the prompts sent to the LLM.

## Errors

`InternalError`s, raised at startup or during the conversation:

| Code | Cause |
|---|---|
| `STEP_NOT_FOUND:<id>` | A `next` targets a step missing from the flow (`check_flow` catches it first: `FLOW_NEXT_UNKNOWN`) |
| `NEXT_NOT_FOUND:<step>:<value>` | `run` returned a value without a key in `next` |
| `EXTENSION_NOT_FOUND:<key>` | `require_extension` on an extension never set |
| `EXTENSION_KEY_CONFLICT:<key>` | Two extension classes share the same `__key__` |
| `TYPE_CONFLICT:<class>` | An extension has the name of another `Polymorphic` class |
| `TEXT_CODE_DUPLICATED:<class>` | Two `TextCode`s share a name |
| `TRANSLATION_MISSING:<language>:<keys>` | A code without translation in this language |
| `TRANSLATION_UNKNOWN:<language>:<keys>` | A translation whose code doesn't exist |
| `TRANSLATION_DUPLICATED:<language>:<class>` | The same class translated in two files |
| `TRANSLATION_FILE_MISSING:<language>:<entry point>` | A package declared in `interactive_support.locales` without its `locales/<language>.json` |

The structure errors (`FLOW_*`) are in [testing.md](testing.md).
