# Testing a flow

- **The only fake is the LLM**, scripted by flow-test. No test calls a real LLM. CANCEL also fakes the geocoding API it calls, in its `conftest.py`.
- **No mock** (`unittest.mock`), **no `cast`**, **no `pytest.skip` nor `xfail`**: ruff rejects them in tests. A test runs, or it is deleted.
- **No tests on `domains/order`**: it will be rewritten. A domain function you add is tested through the flow's paths.
- **A test adapts to the code, never the other way round.** To plug a fake, look for a solution in flow-test first. If code outside the flow must change, show the minimal diff and ask first.
- **pyright is strict on `flows/`**, tests included, and `# type: ignore` is disabled. An assumed private access is declared at the top of the file, with its reason: `# pyright: reportPrivateUsage=false` (the `conftest.py` copied from DAMAGED does it).

Outside the flow, `packages/core/tests/test_checks.py` also runs on it: `check_flows()` (every `Issue` has its flow and its `IssueChoice`) and `check_translations()` (every `TextCode` is translated in every language). So does the opening test to adapt (SKILL.md, step 2).

# `flow-test`: testing a flow

A flow test plays **a full conversation** in the real engine, as the front would, with a scripted LLM. Each turn asserts **everything**: what the bot said, the next question, and what the LLM received.

```python
from interactive_support_flow_test import (
    FlowTest,
    Choice,
    Confirm,
    Text,
    Photo,
    Form,
    check_flow,
    reply,
)
```

The flow declares flow-test in its `dev` group. Tests go in `flows/<flow>/tests/test_<flow>.py`, next to a `conftest.py` copied from DAMAGED: it isolates the in-memory orders, so each test starts from the seed orders. CANCEL's also fakes the geocoding API of its `geo` package (`geocoded` fixture): don't copy that part. The reference is `flows/cancel/tests/test_cancel.py`; `flows/damaged/tests/test_damaged.py` shows the photo.

## In short

```python
def test_cancel_for_a_service_issue():
    reason, details = (
        "Toujours pas préparée après 10 jours",
        "Personne ne répond au téléphone",
    )
    before = order("#CMA_002")
    t = FlowTest(
        CANCEL_FLOW,
        order_number="#CMA_002",
        language=Language.FR,
        said=[CancelCode.ASK_PROPOSAL],
        next=Choice(
            CancelStep.PROPOSAL_IN_PREPARATION,
            [CancelProposal.CANCEL, CancelProposal.CHANGE_ADDRESS],
        ),
    )

    t = t.choose(
        CancelProposal.CANCEL,
        said=[CancelCode.ASK_CANCEL_REASON],
        next=Text(CancelStep.CANCEL_REASON),
    )

    t = t.write(
        reason,
        llm=[
            reply.classify(
                {"cancel_reason": reason}, reply.yes_no(SERVICE_ISSUE_QUESTION, True)
            )
        ],
        said=[ServiceIssueApology(reason=reason), CancelCode.ASK_SERVICE_DETAILS],
        next=Text(CancelStep.SERVICE_DETAILS),
    )

    t.write(details, said=[CancelCode.ORDER_CANCELLED], next=END)

    cancellation = orders.Cancellation(reason=reason, details=details)
    assert order("#CMA_002") == before.model_copy(
        update={"status": orders.OrderStatus.CANCELLED, "cancellation": cancellation}
    )
```

When several tests share the same beginning, factor it into a function returning the typed `FlowTest`: `def delivered() -> FlowTest[Photo]` in DAMAGED. The type is the question pending: `FlowTest[Text]`, `FlowTest[Confirm]`, `FlowTest[Choice[CancelProposal]]`.

## A turn

`FlowTest(flow, order_number=..., language=...)` starts the flow as if the opening had just ended. Then each answer plays one turn:

| Question asked (`next`) | Answer |
|---|---|
| `Choice(step, options)` | `t.choose(option)`: a member of `options` |
| `Confirm(step, value, location)` | `t.confirm(True)` or `t.confirm(False)`. `location` only when the question shows a map |
| `Text(step)` | `t.write("customer's text")` |
| `Photo(step)` | `t.send_photo("data:image/jpeg;base64,...")`: the photo as the front sends it |
| `Form(step, fields, values)` | `t.fill({Field.X: "...", ...})`: every field, the kept pre-filled ones included, as the front sends it. `values` lists only the pre-filled fields |
| `END` | nothing more: the flow is over |

Each turn, the start included, takes:

| Argument | Content |
|---|---|
| `said` | **required**. Everything the bot said during the turn, in order: the `TextCode`s, and the generated messages as their `Communication`, facts included |
| `next` | **required**. The next question, **content included**: the options in order, the value to confirm. `END` if the flow is over |
| `llm` | one reply per LLM call of the turn, in call order. Empty by default |

Always write `t = t.choose(...)`: `t`'s type follows the question asked, and pyright rejects an answer that doesn't match it (`write` on a `Choice` or a `Photo`, an option from another enum, an answer after `END`).

An answer rejected by the flow (`InvalidAnswer`) asks the same question again **without** its `pre_hook`: `said=[CancelCode.ADDRESS_UNREADABLE], next=Text(CancelStep.NEW_ADDRESS)`.

Every turn, `FlowTest` also checks that the `Conversation` survives a JSON round-trip, and the next turn starts from that JSON.

## The scripted LLM

`FlowTest` replaces the LLM during each turn (`Classify.run`, `llm.generate._call`, `communication.generate._write`). Each call of the turn must be scripted in `llm`, **with what it must receive** (`given`):

| Call in the flow | Scripted reply |
|---|---|
| `llm.generate(instruction, input, Output)` | `reply.generate(given=Input(...), output=Output(...))` |
| `llm.classify(**texts)....run()` | `reply.classify({"name": "text"}, answer_1, answer_2...)`: one answer per question, in order |
| `.yes_no(QUESTION, yes=..., no=...)` | `reply.yes_no(QUESTION, True)`, or `reply.yes_no(QUESTION, True, confidence=0.2, true_probability=0.6)`, both given |
| `.choose(QUESTION, Enum)` | `reply.choose(QUESTION, Enum.MEMBER)`, or `reply.choose(QUESTION, Enum.MEMBER, confidence=0.4, probabilities={...})` with **every** member |
| `.score(QUESTION, Enum)` | `reply.score(QUESTION, Enum.LEVEL)`, or with `value=`, `confidence=` and `probabilities=` all given |
| `communication.generate(ctx, Message(...))` | nothing: the reply is automatic, assert `Message(...)` in `said` |
| an `llm.Image` as input | the `given` is built the same way: `ReportInput(photo=llm.Image(PHOTO), ...)` |

A `classify` question is the flow module's constant (`SERVICE_ISSUE_QUESTION`): the test imports it and passes it to its reply.

The member alone means "the LLM is certain". To test a threshold (`confidence >= 0.7`…), give the confidence and the probabilities: the fake never makes them up.

## Rules

- **One structure test per flow**: `def test_structure(): check_flow(MY_FLOW)`. It checks what no path shows: unique ids, existing targets, reachable steps, no loop without a question, dict `next` covered by the `run`'s annotation.
- **One test per path of the flow.** `make test` fails while a transition is taken by no `FlowTest`: a direct `next`, or each key of a dict `next`. pytest still prints "N passed": what counts is the exit code and the "flow coverage: transitions never taken" block, which lists them. A `pytest.mark.parametrize` covers several statuses leading to the same message.
- **Write the expectations from the flow**, never by copying a failing test's output: the test would prove nothing anymore.
- **Check the domain state at the end**: comparing to `before.model_copy(update={...})` also proves nothing else changed.
- **Set up a state through the domain**, not by touching its data: `orders.cancel("#CMA_001", ...)` for a cancelled order.
- **No `TextCode` declared in a flow's test**, and never an import of `interactive_support_core`.

# Errors

Each one fails the test with this code.

| Code | Cause |
|---|---|
| `TURN_MISMATCH` | The turn doesn't match `said` / `next`: the message shows expected and actual |
| `UNSCRIPTED_LLM_CALL` | An LLM call without a scripted reply: the message shows what it received |
| `UNUSED_LLM_REPLY` | A scripted reply that no call of the turn consumed |
| `LLM_CALL_MISMATCH` | The call doesn't receive the scripted `given`, or doesn't ask the same questions |
| `LLM_REPLY_INCOMPLETE:<Enum>` | `probabilities=` doesn't give every member of the enum, or gives others |
| `ANSWER_MISMATCH` / `ANSWER_AFTER_END` | The answer doesn't match the question (option not offered) / the flow is over |
| `NEXT_MISSING_OPTION` | An offered option (or `True`/`False` of a `Confirm`) has no key in the step's `next` |
| `FLOW_NOT_REGISTERED` | The flow isn't declared in its pyproject's entry points, or `make install` wasn't rerun |
| `CONVERSATION_NOT_SERIALIZABLE` | The conversation doesn't survive a JSON round-trip: an extension holds something non-serializable |
| `MANY_PENDING_ACTIONS` | More than one pending action: a flow asks one question at a time |

Structure errors, raised by `check_flow`:

| Code | Cause |
|---|---|
| `FLOW_STEP_DUPLICATED` | Two steps share an id |
| `FLOW_NEXT_UNKNOWN` | A `next` targets a step missing from the flow |
| `FLOW_NEXT_UNTYPED` | A dict `next` whose `run` isn't annotated (a lambda, for instance) |
| `FLOW_NEXT_NOT_EXHAUSTIVE` | The `next` keys aren't exactly the values `run` can return: `missing=` and `extra=` list them |
| `FLOW_STEP_UNREACHABLE` | A step no path reaches from the first one |
| `FLOW_LOOP_WITHOUT_ASK` | A loop of `Step`s without an `AskStep`: it would run forever |

`check_flows` errors, raised by `test_checks.py` and at CLI startup (the translation ones are in [flow.md](flow.md#errors)):

| Code | Cause |
|---|---|
| `FLOW_MISSING:<issue>` | An `Issue` without an installed flow |
| `FLOW_DUPLICATED:<issue>` | Two flows for the same `Issue` |
| `ISSUE_CHOICE_MISSING:<issue>` | An `Issue` missing from `IssueChoice`: the opening can't offer it |
