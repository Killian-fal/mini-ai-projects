---
name: new-flow
description: Create the conversation flow of a new customer problem (Issue) in interactive-support, from the request (often a diagram) to a tested, registered flow — the flows/<flow> package, its steps, TextCodes and translations, its LLM calls (tools.llm, tools.communication), its flow-test tests, and the few files outside the flow that register it. Also use it to add steps to an existing flow. Explains every error code a flow or its tests can raise (FLOW_*, TURN_MISMATCH, LLM_*, TRANSLATION_*, EXTENSION_*...).
---

# Creating a flow

A customer writes to an online store's support. The opening (already written, in core) detects their language, their problem (`Issue`) and their order number, then hands over to **the flow of that problem**: steps that ask the customer questions, query the LLM and act on the orders. One flow per `Issue`.

**CANCEL** (`flows/cancel`) is the reference: copy its conventions instead of inventing new ones. **DAMAGED** (`flows/damaged`) shows a photo and the multimodal LLM. Trust the code over this doc when in doubt.

## Golden rules

1. **A flow imports only flow-api and its domains**: `interactive_support_flow_api`, `interactive_support_domain_order`. Never `interactive_support_core` (ruff rejects it in `flows/`), never `interactive_support_flow_api._internal`, never `dspy`. The last two are not enforced by any tool: it's on you.
2. **No hard-coded text.** Everything the customer sees is a `TextCode` translated in `locales/en.json` and `locales/fr.json`. Errors carry codes, never sentences: `InvalidAnswer(LateCode.DATE_UNREADABLE)`. Only exception: the text the LLM writes with `communication.generate`.
3. **What a flow keeps between two steps goes in an `Extension` of the context**, nowhere else: the engine keeps nothing, everything is rebuilt from the conversation's JSON at each answer.
4. **The LLM is only reached through `tools.llm`** (`classify`, `generate`) **and `tools.communication`.**
5. **The only fake in tests is the LLM** (and the geocoding API in CANCEL). No mock, no `cast`, no `skip`/`xfail`: ruff rejects them. A test adapts to the code: never change code outside the flow for a test without asking.
6. **Outside the flow, touch only the five registration places** (step 2) **and the domain** when a business action is missing (step 0).
7. **No silent questionable choice.** A need the request doesn't cover (a forgotten order status, a missing domain action): make the simplest choice, then report it.

## Commands

```bash
make install   # uv sync --all-packages: rerun after any pyproject change (entry points included)
make format    # ruff format
make check     # ruff check + pyright (strict on flows/ and the tests)
make test      # pytest + flow coverage: fails if a transition of a flow is never taken
uv run cli     # a conversation in the terminal, with the real LLMs (.env with the keys of .env.example)
```

**Done** = `make format`, then `make check` and `make test` green.

## The checklist

The examples use a `late` flow (`Issue.LATE`, `LATE_FLOW`, `LateCode`): replace with yours.

### 0. Understand the request

You are usually given a diagram: the questions, the branches, what happens at the end. Before writing:
- **Every order status must lead somewhere**, and an order may not exist. If the diagram only has two branches, add the missing messages (`ORDER_NOT_FOUND`, a cancelled order…), each named after what it says, then report them.
- **Spot the LLM calls**: decide (`classify`), extract or draft an object (`generate`), write to the customer (`communication`). See [llm.md](references/llm.md).
- **Spot what touches the orders.** The domain is `domains/order` (`import interactive_support_domain_order as orders`, as in CANCEL), in memory for now, **with no tests of its own**:
  - functions: `get` (`None` when the order doesn't exist), `create`, `update`, `delete`, `cancel`, `update_address`, `update_delivery_mode`, `report_damage`;
  - frozen models: `Order`, `Cancellation`, `Damage`, `OrderStatus` (`NOT_PREPARED`, `IN_PREPARATION`, `SHIPPED`, `DELIVERED`, `CANCELLED`), `DeliveryMode`;
  - rules: an order can only be modified before it ships, a damage only reported on a delivered order. Otherwise `OrderError("ORDER_NOT_MODIFIABLE:<n>")`, `ORDER_NOT_DELIVERED`, `ORDER_NOT_FOUND`. **A flow checks the status before acting and never catches `OrderError`**;
  - a missing business action goes in the domain: a function, a frozen model if needed, a coded `OrderError`. If no domain fits the need, report it before creating one.

| Seed order | Status | Delivery |
|---|---|---|
| `#CMA_001` | `NOT_PREPARED` | `HOME` |
| `#CMA_002` | `IN_PREPARATION` | `RELAY_POINT` |
| `#CMA_003` | `SHIPPED` | `HOME` |
| `#CMA_004` | `DELIVERED` | `HOME` |

### 1. The flow's package

```
flows/late/
├── pyproject.toml
├── src/interactive_support_flow_late/
│   ├── __init__.py          # from .flow import LATE_FLOW ; __all__ = ["LATE_FLOW"]
│   ├── py.typed             # empty: the package is typed
│   ├── flow.py              # docstring, LateStep, the choices' TextCodes, LATE_FLOW
│   ├── code.py              # LateCode: every message of the flow
│   ├── status.py            # order_status, the first step (copied from CANCEL)
│   ├── <theme>.py           # a theme's step functions, its extensions, its LLM inputs/outputs
│   └── locales/
│       ├── en.json
│       └── fr.json
└── tests/                   # no __init__.py
    ├── conftest.py          # copied from DAMAGED: isolates the in-memory orders
    └── test_late.py
```

`pyproject.toml`:

```toml
[project]
name = "interactive-support-flow-late"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "interactive-support-domain-order",
    "interactive-support-flow-api",
    "pydantic>=2.13.5",
]

[dependency-groups]
dev = [
    "interactive-support-flow-test",
]

[project.entry-points."interactive_support.flows"]
late = "interactive_support_flow_late:LATE_FLOW"

[project.entry-points."interactive_support.locales"]
late = "interactive_support_flow_late"

[build-system]
requires = ["uv_build>=0.11.28,<0.12.0"]
build-backend = "uv_build"
```

The flow is found through these entry points, never imported: they only exist after `make install`.

### 2. The five places outside the flow

The flow doesn't work until all of them are done. `make test` catches most of them.

| File | What | Otherwise |
|---|---|---|
| `packages/flow-api/src/interactive_support_flow_api/model/context/issue.py` | `LATE = "LATE"` in `Issue` | the flow can't declare its `issue` |
| `packages/core/src/interactive_support_core/opening/code.py` | `LATE = Issue.LATE` in `IssueChoice`, before `OTHER` | `ISSUE_CHOICE_MISSING:LATE`: the opening can't offer it to the customer |
| `packages/core/src/interactive_support_core/opening/locales/{en,fr}.json` | the translation of `IssueChoice.LATE`, from the customer's point of view ("My order is late") | `TRANSLATION_MISSING` |
| `flows/bom/pyproject.toml` | `"interactive-support-flow-late"` in `dependencies` | an application installed outside the workspace (wheel, Docker) doesn't ship the flow. **Nothing catches it in dev**: `uv sync --all-packages` installs every member |
| `pyproject.toml` (root) | `interactive-support-flow-late = { workspace = true }` in `[tool.uv.sources]` | `make install` fails: bom depends on a workspace member without a source |

**Then an opening test to adapt**: in `packages/core/tests/opening/test_handler.py`, each `reply.choose(ISSUE_QUESTION, ..., probabilities={...})` gives the probability of **every** member of `IssueDetection`, which now has one more. Add `LATE = IssueDetection["LATE"]` next to `DAMAGED`, and `LATE: 0.0` to each dict (otherwise `LLM_REPLY_INCOMPLETE:IssueDetection`).

`IssueDetection` is built from the installed flows: nothing to change there, but the flow's `description` is what the opening's LLM reads to recognize the problem.

### 3. Install

```bash
make install
```

Without it: `FlowTest` raises `FLOW_NOT_REGISTERED:LATE`, and `check_flows` raises `FLOW_MISSING:LATE`.

### 4. Write the flow

Follow [flow.md](references/flow.md), with CANCEL open beside it:
1. `code.py`: `LateCode`, one code per message (`ASK_<STEP>` for each question, one code per ending).
2. `flow.py`: the docstring, `LateStep(StepId)`, the choices' `TextCode`s, then `LATE_FLOW` with `ORDER_STATUS` first.
3. The theme modules: one function per step, the extensions, the LLM inputs and outputs, the `classify` question constants ([llm.md](references/llm.md)).
4. `locales/en.json` and `locales/fr.json`: every `TextCode` class of the flow, every member.

### 5. Test

Follow [testing.md](references/testing.md):
- `conftest.py` copied from DAMAGED;
- `test_structure` with `check_flow(LATE_FLOW)`;
- one test per path of the flow, until `make test` reports no transition left;
- the domain state checked at the end of the paths that act.

### 6. Check

```bash
make format
make check
make test
```

To try it with the real LLMs: change the `msg` in `packages/cli/src/interactive_support_cli/main.py` to a first message about your problem (with a `cma_00X` number matching the status you want), then `uv run cli`. For a photo, give a file path: the CLI sends it as a data URI, like the front. Put `msg` back afterwards.

### 7. Report

- A diagram of the flow (ASCII): the steps, the branches, the messages.
- What you added that the request didn't contain: messages, statuses, domain functions.
- What isn't verified: the tests never call the real LLM.

## References

| You want to… | Read |
|---|---|
| Write the steps: `Step`, `AskStep`, `next`, questions, `InvalidAnswer`, extensions, `TextCode`s, CANCEL's conventions | [references/flow.md](references/flow.md) |
| Have the LLM decide, produce an object, or write to the customer | [references/llm.md](references/llm.md) |
| Test the flow with flow-test | [references/testing.md](references/testing.md) |

For an unknown error code: `grep -rn CODE .claude/skills/new-flow/`, then the code.

## Keeping this skill up to date

It covers writing a flow, nothing else. A change to flow-api, flow-test, the domain or CANCEL's conventions updates the matching reference in the same commit.
