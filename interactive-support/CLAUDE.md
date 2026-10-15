# CLAUDE.md

Rules for code agents in this repository: what must never be done, the pitfalls already hit, and the processes to follow.
It does not say where things are: read the code for that. The front end has its own `CLAUDE.md` in its folder: read it
before touching the front.

Read only what the change touches, trace it end to end, then act. Do not re-read the whole repository for each request.

## Operating principles

1. **Layers point one way.** The flow API package holds only what a flow may touch. Everything a flow must not touch
   lives in the engine (core). A flow depends on the flow API and on the domains it uses, never on the engine, another
   flow, or the flow API's internal module. A domain is pure business logic and depends on no project package. An
   application (REST API, CLI) depends on the engine and the bill-of-materials package, never on a flow.
2. **Discovery by entry points only.** Flows and translation files are found through package entry points. Never use
   forced imports, scans by package prefix, or `Path(__file__)`.
3. **The engine is stateless.** Every answer rebuilds everything from the Conversation's JSON. What a flow keeps
   between steps goes into an extension of the flow context, nowhere else. There is no database in V1.
4. **Codes, not text.** Everything the customer sees and every error carries a code: a `TextCode` member, or
   `InternalError("CODE:detail")`. Translations are back-end JSON files next to the code that defines the codes. They
   are applied only at the output boundary (API, CLI). The engine stores codes, and the front translates nothing. Only
   exception: the text the LLM writes for the customer through the communication tool.
5. **The API contract is typed for the front.** The front generates its TypeScript types from the OpenAPI document. The
   API exposes typed mirrors (DTOs, discriminated unions on `role` and `type`), never a core model, neither in a
   request nor in a response.
6. **Flows are written by agents.** CANCEL is the reference flow that agents copy. Judge every change by "would an agent
   copying this get it right?" Prefer uniform conventions to clever ones, and guards that fail loudly to rules that live
   only in documentation.

## Processes

**Create or change a flow.** Load the `new-flow` skill and follow it: it is the only documentation of how to write a
flow. A change to the flow API, flow-test, a domain or CANCEL's conventions updates the matching skill reference in the
same change.

**Change what the API sends to the front.** Work in this order:

1. The flow API model.
2. The engine, if a message or an action changes.
3. The API's DTO mirror and its mapper.
4. The contract tests: the OpenAPI test lists every message role and action type.
5. Start the API and regenerate the front's schema with its generation script. Never edit the generated schema by hand.
6. Let the TypeScript compiler list what breaks, then fix the front.

To show something new in the conversation, extend a question and its action (the front's actions registry is the
extension point) before adding a new message role.

**Definition of done (back end).** `make format`, then `make check` and `make test` green. `make test` also fails when a
transition of a flow is taken by no `FlowTest`. After any `pyproject.toml` change (dependency, entry point), run
`make install`, or a new flow or translation file is not found. The front end has its own commands. `make eval` is not
part of it.

**Evaluate an LLM call.** A test never calls the real LLM; an eval does, to measure how well an LLM call does its job.
Evals live in an `evals/` folder next to `tests/`, each marked `@pytest.mark.eval`: `make test` skips them and
`make eval` runs them, with MLflow up and the dspy cache off so that each run measures today's model. The developer
runs them, not an agent. The routing of the opening is evaluated in the engine, the other LLM calls of a flow in the
flow. Cases are in French, written and labelled by a human, never copied from a model's output. An eval reports a
score: never relabel or drop a case to raise it, report the drop.

**Blocking issue.** When something blocks you (a tool failing in a non-obvious way, a rule contradicting the task, a
hidden coupling), stop and explain it to the developer instead of working around it. Once it is solved together,
propose a rule for this file that would have prevented it. Write the rule and its reason, never file names, versions or
counts that will rot. Add it only once the developer agrees.

## Must not do

### Architecture

- Import the engine from a flow (ruff rejects it), or the flow API's internal module, `dspy` or an LLM client. A flow
  reaches the LLM only through the `llm` and `communication` tools.
- Keep conversation state outside the Conversation: module globals, caches, singletons.
- Write customer-visible text or error messages in code, or translate inside the engine or a flow.
- Accept or return a core model in the API: its `__type__` field lets a client rebuild another class.
- Give two `Polymorphic` subclasses the same class name anywhere in the workspace: the type registry is keyed by class
  name (`TYPE_CONFLICT`).
- Add a dependency without asking. Try the standard library first.
- Add persistence or a database before the developer asks for it.

### Engine pitfalls

- `InvalidAnswer` discards every change the step made to the context, then asks the same pending action again,
  unchanged and without its `pre_hook`. Never rely on context set before the raise.
- A question is built several times: when it is asked, when the answer is parsed, and by the tests. It must rebuild
  identically from the context: no randomness, no side effect.
- A step that acts (changes an order) never asks a question. The asking steps before it only save the answers.

### Tests

- Write integration tests, input to output. The only fakes are the LLM, scripted with flow-test, and external HTTP APIs,
  replaced at their private seam. No `unittest.mock`, no `cast`, no `skip` or `xfail` (ruff rejects them), and never
  fake an internal collaborator.
- Fake an external call by patching the private function inside its module. When the package re-exports a public
  function with the module's name, reach the module through `import_module`. The fake then works however the caller
  imported the public function.
- Never reshape production code to make it testable without asking: show the minimal diff first. Already refused:
  a class method that only delegates to a private module function, and replacing parameters with a parameter object.
- Write no tests on the in-memory order domain (it will be rewritten), and no test that calls the real LLM:
  that is an eval.
- Write expectations from the flow, never by copying the output of a failing test.
- pyright is strict on flows, flow-test, the API and every test and eval folder, and `# type: ignore` is disabled.
  Declare a deliberate private access at the top of the file, with its reason: `# pyright: reportPrivateUsage=false`.

### Documentation and language

- Write no README and no architecture document. The only documents are this file (rules), the front's `CLAUDE.md` and
  guideline, and the `new-flow` skill. Put nothing about the API, the CLI or the engine in the skill: its tokens are paid
  at every flow creation.
- Code, comments, LLM prompts and documentation are in English. Every customer-facing code is translated in every
  supported language; the translation check fails otherwise.

### Working with the developer

- Make no silent questionable choice: take the simplest option, then report it.
- Do not widen the scope of a request, and do not commit unless asked.
