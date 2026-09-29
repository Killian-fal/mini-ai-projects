# CLAUDE.md

Sentinel looks for indirect prompt injections in Common Crawl web pages.
The backend selects and downloads pages, stores them, then has them scored by a paid model (Jev).
The front displays the results based on the backend's OpenAPI contract.

This file lists what an agent **must not do** and **how to work in this repo**.
It does not describe the files: read them. The detailed architecture rules live in
`guidelines/` (one page for the backend, one for the front) and **are authoritative**: read the one
for the side you are touching before writing code.

## Continuous improvement rule

When you get stuck (a tool that lies, a command that breaks the environment, an error that cost you
time, an implicit rule discovered too late):

1. Stop and explain the problem to the dev. Do not silently work around it.
2. Once the problem is understood, **propose together** a line to add to the "Known pitfalls"
   section below, so it does not happen again.
3. Write that line as a durable rule: the cause and the reflex to have. **No** file paths, current
   figures, dates or branch names: that information ages fast and makes the file wrong.

## Never

- **Lose data.** The Mongo database holds hours of scanning that cannot easily be redone. Never
  delete, empty or recreate a database, a collection or a Docker volume, and never rename what is
  used to find them, without explicit approval. A schema change is announced before it is applied.
- **Overwrite the dev's work in progress.** The working tree often contains uncommitted changes,
  sometimes a migration in progress. Never run `checkout`, `reset`, `stash` or `clean` without
  asking. Check paths before editing. Only commit when asked to.
- **Get the IP banned by Common Crawl.** Its CDN bans the IP beyond an undocumented request rate.
  Keep few downloads in parallel, never run two scans at the same time, and remember that index
  reads also count toward that rate.
- **Spend money without saying so.** Every call to Jev costs money. No bulk analysis without
  approval, and give the cost estimate beforehand. Tests never call a real model.
- **Silently reduce recall.** A prefilter, a cache or a cutoff that saves calls can also make us miss
  injections. That trade-off is measured and decided with the dev.
- **Strip non-standard HTTP headers from what is sent to the model.** According to the reference
  study, they are the main attack channel.
- **Commit a secret.** Keys go in the backend's `.env`, which is ignored by git. The `.env.sample`
  lists the expected variables.
- **Add a dependency** (including a test one) without asking.
- **Force a tool to pass**: no `noqa`, no `type: ignore`, no disabled rule to get through. Fix the
  code, or settle the rule with the dev in the config.
- **Run a tool anywhere other than its project root** (backend root or front root). From another
  directory, config paths resolve incorrectly and the tool reports errors that do not exist.

## How to work

- **Measure before deciding.** Filtering, cost or detection choices rely on a measurement made on
  our own data, not on intuition. Before starting a study, check whether `docs/` has already done
  it.
- **The simplest solution that holds.** No speculative abstraction, the shortest diff. A deliberate
  simplification with a known limit is marked with a `ponytail:` comment that names that limit.
- **An API contract change propagates in a fixed order**: modify the backend, start the API,
  regenerate the front types with the provided script, then let the compiler list the front code to
  fix. Generated types are never edited by hand.
- **Nothing is done until all checks pass**: format, lint, types, file size and tests, from the root
  of the project concerned, with no warnings at all. Each side's README gives the commands.
- **For a question about an external library or API**, read its documentation or its sources
  instead of guessing.
- Answer in French, with all the accents.

## Known pitfalls

- `http.client.IncompleteRead` (connection dropped during the read) is not an `OSError`. In a
  worker, any uncaught exception kills the whole run.
- Common Crawl adds headers itself (`X-Crawler-*`, and CDN ones like `x-amz-`). They must be
  excluded before any keyword search on headers, otherwise false positives explode.
- A Mongo `$in` with a very large list exceeds the 16 MB document limit: split the list into
  batches.
- A package without `py.typed` is seen as untyped by mypy in other packages, and every import
  becomes an error.
- If not given `length`, warcio buffers the payload into a temporary file that it never closes.
  Pytest reports it with a `ResourceWarning` that fails the test.

## Code practices: backend

In addition to `guidelines/backend.md`.

### Package structure

- A package wraps **a single external resource** (Common Crawl, Mongo, the model provider).
  Packages never import each other. Only the apps assemble them.
- `__init__.py` is a **facade**: re-exports and `__all__`, with no logic at all. Each symbol is
  imported from the module that defines it, never indirectly through another module's re-export.
- Data types (`frozen=True, slots=True` dataclasses) live in a models module. Public exceptions have
  their own module and are exported by the facade: an exception that leaves the package is part of
  its public API.
- Order within a module: imports, constants, public functions, then private helpers (`_name`)
  below.
- A package imports without configuration: clients and settings are built on first use, never at
  module load time.
- A new package has its own `py.typed`.

### Style

- Comments and docstrings **in English**.
- Comments: only on a line that looks useless but is not, or to flag a coupling that is invisible
  from the file. No comment that tells the story of a decision or its history. Short docstrings, or
  no docstring at all.
- Unreachable code: `raise AssertionError`, never a generic `Exception`.
- An exception's message is written directly in the `raise`, without an intermediate `msg`
  variable.
- Programming errors stay visible: never wrap them in a domain exception.

### Tests

- **Test end to end through the public API**: the package facade or the app endpoint. Never a
  private function. These tests survive refactors, unit tests do not.
- **Only mock at resource boundaries**, and locally:
  - the network with a real local HTTP server that behaves like the real one (`Range` requests,
    error codes, dropped connections);
  - data files (parquet, WARC…) generated in `tmp_path` by the real libraries, with no versioned
    binary file;
  - the real database in a container.

  All the code between these boundaries runs for real.
- **A fake refuses what the real thing refuses.** An overly permissive fake makes the test
  tautological.
- Unit tests are reserved for **pure logic with many cases** (parser, score computation, selection
  rules), where end-to-end combinations would be too numerous.
- One test = one behavior, named after that behavior. Not one test file per source file.
- Test helpers live in the test file, or in a fixture that returns a function. Never imported from
  the `conftest`.
- Production code never serves the tests (for example, no cache reset exported for them).
- No real waiting: replace `time.sleep` during the test, and make the test server poll quickly so it
  stops fast.
- **A test you have never seen fail proves nothing**: break the behavior, check that the test fails,
  then restore the code.

## Code practices: front

Coming soon. Until then, `guidelines/frontend.md` is authoritative.
