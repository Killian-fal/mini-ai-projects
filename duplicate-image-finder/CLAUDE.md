# CLAUDE.md

Guide for code agents working on this repo. This file does **not** describe the code structure (which changes often) — it lays down **prohibitions** and **durable operating principles**.

> Read this file before making any change. When in doubt, ask the developer rather than assume.

---

## 1. Operating principles

These principles describe **how** the repo works, independently of the current files. Any contribution must respect them.

- **Centralized configuration.** All runtime parameters (input/output folders, batch size, number of workers, etc.) go through the YAML configuration file loaded at startup. Never reintroduce hard-coded paths or parameters elsewhere in the code.

- **Persistence through the repository layer only.** No direct access to the vector database from application code. A new access need = a new method on the repository layer, not a workaround.

- **Centralized device detection (cuda / mps / cpu).** Never hard-code a device in a leaf module — always go through the dedicated utility.

- **Vision model ⇄ embedding dimension: strict coupling.** Changing the model checkpoint without aligning the vector dimension (and vice versa) silently corrupts the existing table. Both change together, or neither does.

- **Extended image format support (HEIC, etc.) is enabled globally, at package import.** Do not duplicate it in leaf modules, do not disable it.

---

## 2. DO NOT

- **Never use `pip` or `python` directly** to install or run the project. Always go through **`uv`** (`uv run`, `uv add`, `uv sync`). Corollary: **never edit the lockfile by hand**.

- **Do not interpolate strings** into the repository's `where` clauses without escaping. Risk of injection and of crashing on apostrophes / special characters in paths.

- **Do not desynchronize** the vision model checkpoint and the embedding dimension (see principles).

- **Do not commit / push** without an explicit request from the developer, even when a change "seems done".

---

## 3. When an uncovered blocker appears

If an agent runs into a recurring or counter-intuitive trap (environment incompatibility, subtle behavior of a dependency, tool behaving unexpectedly) **not covered** by the sections above, it **must**:

1. **Report the case to the developer** before attempting a workaround.
2. **Propose an addition to this `CLAUDE.md`** once the cause is understood.
3. **Phrase the rule in a durable way**: no specific package version, no file path, no copy-pasted error message. Only the **general rule** to apply ("do not do X because Y", "always go through Z"). The guidance must stay valid even as the underlying cause evolves.

## Boil the ocean
The marginal cost of completeness is near zero with AI. Do the whole thing. Do it right. Do it with tests. Do it with documentation. Do it so well that Killian is genuinely impressed – not politely satisfied, actually impressed. Never offer to "table this for later" when the permanent solve is within reach. Never leave a dangling thread when tying it off takes five more minutes. Never present a workaround when the real fix exists. The standard isn't "good enough" – it's "holy shit, that's done." Search before building. Test before shipping. Ship the complete thing. When Killian asks for something, the answer is the finished product, not a plan to build it. Time is not an excuse. Fatigue is not an excuse. Complexity is not an excuse. Boil the ocean.