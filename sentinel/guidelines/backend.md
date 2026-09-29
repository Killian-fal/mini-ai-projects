# Backend — how to organise it

One rule above all: **a boundary is held by a tool, or it does not exist.**
What no tool can check goes into a skill the agent loads before writing.

## Shape

```
backend/
  <root manifest>        workspace members + tool config. Zero code.
  tools/                 the one or two checks the toolchain lacks
  packages/<name>/       one external concern each
    <manifest>
    src/<name>/__init__  façade
    src/<name>/…
    tests/
  apps/<app>/            the composition root. Depends on every package;
    src/<app>/           nothing depends on it.
    tests/
```

Each package and the app is its own project with its own manifest, resolved
together as one workspace with one lockfile.

## Packages

- **One package = one external concern**: the database, the object store, the
  model provider. Never one per layer. Code that wraps nothing outside the
  process is a module, not a package.
- **Packages never import each other.** Only the app knows them all. A data
  type may cross, never behaviour, and that crossing is decided, not drifted
  into.
- **The entry point is a façade**: re-exports and the public list. No logic.
  What it exports is public; everything else does not exist from outside.
- **An exception that crosses the package boundary is public API.** Name it in
  the façade, decide it, never add one in passing. The error wall also covers
  reading the environment. Programming errors stay loud: never wrap them.
- **A package imports without configuration.** Settings and clients build on
  first use, never at module load. Otherwise every other package's tests need
  this package's secrets to read a type.
- Adding a package: the folder, the manifest, and its source root declared to
  the type checker. Forgetting the last turns every import into a missing stub.

## The app: three roles, split by resource

Same file name in each of `routes/`, `services/`, `mappers/`.

| Role    | Does                                                        | Must not                                    |
| ------- | ----------------------------------------------------------- | ------------------------------------------- |
| Route   | reads the request, calls **one** service or mapper, sets the status code | import a package: `grep <package> routes/` stays empty |
| Service | orchestrates packages. A pass-through is fine; the property matters, not the lines | know the transport |
| Mapper  | free functions, package models → API schemas                | touch I/O                                   |

Only rules of the transport boundary itself (unsupported media type, payload
too large) may live in a route. Background work is its own module, called by
the task launcher, never by a route.

## Persistence

- Nothing loads lazily on an asynchronous engine. Explicit joins, explicit
  pairs.
- A column holding structured data is converted by a declared type on both
  the write and the read. Manual serialisation handles one direction and
  silently returns raw dictionaries in the other, and the type checker sees
  nothing.
- No migration tool until a database holds data worth keeping. Until then a
  schema change recreates the database, and **that is announced before it is
  done**.

## The toolchain, by role

- **Type checker in strict mode**, with the framework plugin that understands
  data models. Warnings on unreachable code.
- **Linter with every rule on**, then a short explicit ignore list, each entry
  justified. Complexity caps: cyclomatic 8, arguments 5, branches 8, returns 4,
  statements 30.
- **Formatter** in check mode.
- **File length cap**: 300 lines, hard fail. The toolchain lacks it; a
  ten-line script in `tools/` provides it.
- **Test runner** against a real database in a container.
- **Pre-commit and CI run the same commands**, always from the backend root,
  always through the workspace runner so the lockfile is the only source of
  tool versions.

Every command from the backend root. Elsewhere, config paths resolve from the
wrong directory and the tool accuses the code of a fault it does not have.

## Tests

- **Mock only what you do not own**, at the network edge. The database runs
  for real. A root test config forbids real model calls, so a forgotten
  override fails loudly instead of passing by calling the provider.
- Enter at the **widest fast boundary**: the endpoint, the package façade.
  Never a private function.
- One test = one behaviour. Never one test file per source file.
- Production code never serves tests: no exported cache reset. A test that
  needs a fresh cache clears it itself, in a fixture.
- Test helpers live in the test file, or as a fixture returning a callable.
  Never imported from the shared test config: works under the runner, breaks
  under the type checker.
- Break the behaviour, watch the test go red, then fix. A test never seen red
  is a wish.

## Before handing back

Format check, lint, type check, tests. From the backend root. Zero warnings or
it is not done.

## Never

- A dependency without asking.
- Logic in a façade.
- A registry, an abstract base, a homemade dependency container, an interface
  with one implementation.
- Conditional or string-quoted imports for typing.
- A suppression comment to get through. Fix the code or settle the rule.
- A comment explaining a decision. Comments mark only the line that looks
  useless and is not, or a coupling invisible from the file.
