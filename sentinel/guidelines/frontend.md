# Frontend — how to organise it

One rule above all: **a boundary is held by a tool, or it does not exist.**
What no tool can check goes into a skill the agent loads before writing.

## Shape

```
src/
  app/              composition root: entry, providers, routes, theme, error
                    boundary. The only place that knows every feature.
  api/              one folder per backend resource
    http             base URL, one `request()`, one error type
    schema           GENERATED from the backend contract, never edited
    <resource>/
      endpoints      the calls, all package-private
      queries        server-state definitions and mutation hooks
      types          aliases picked from the generated schema
      index          façade
  features/<name>/  one product area
    index           exports pages only
    <screen>/       one folder per screen once a feature has several
  ui/               the product's design system: shared visual pieces, no domain
```

## Boundaries, and the tool that holds each

| From       | May import               | Never                    | Held by                          |
| ---------- | ------------------------ | ------------------------ | -------------------------------- |
| `app/`     | features, api, ui        |                          |                                  |
| `features` | api, ui                  | another feature          | restricted-import rule           |
| `api/`     | its own http and schema  | features, ui             |                                  |
| `ui/`      | the design system        | features, api            | restricted-import rule           |
| anyone     | a feature's façade       | a feature's inner files  | package-private annotation + rule |

- Every file a feature does not export from its façade is annotated
  package-private. The linter refuses the import from outside the folder.
- Package-private is strictly the directory: neither parent nor child sees it.
  A sub-folder makes public whatever crosses the new line. Count that before
  splitting.
- Two features meet in `app/` only.
- `ui/` is all public, nothing annotated, and knows no domain: everything
  arrives as props.

Two ways an import rule becomes a decoration:

- a pattern matches a **string**, not a tree: a rule on `**/recipes` also
  catches `api/recipes`. Exclude homonyms explicitly, and verify by writing
  the allowed import as well as the forbidden one;
- two rule overrides on the same file **do not merge**: the last one silently
  replaces the options. Keep scopes disjoint.

## Three natures of component

| Nature    | Right                                                                  | Suffix   |
| --------- | ---------------------------------------------------------------------- | -------- |
| Page      | mounted by the router; reads the URL and the server; picks a screen    | `Page`   |
| Screen    | fills the viewport; receives everything as props; reads no URL, no server | `Screen` |
| Component | everything else                                                        | none     |

- **One file, one exported component**, file named after it. Read the folder,
  not the files, to know where to write.
- A page has a single `return` and a `body(query)` function that picks the
  screen. The shell (title, back link, layout) is written once around the body,
  never in each branch.
- Smaller than a component is not a component: a local function returning
  markup stays a function, no file. What earns a file is written `<LikeThis />`.
- The "this field is empty" guard lives in the section it hides, not in the
  parent. The parent composes without a ternary.
- No boolean prop that switches a whole tree. Two components.
- One error boundary per route.
- A `switch` is exhaustive only if the function declares its return type. No
  compiler option covers it.

## Rendering and state

- **An effect is almost always wrong.** Derivable from props or state: compute
  at render. Triggered by a click: event handler. Only synchronising with the
  outside (a recorder, a timer, a socket) earns an effect, and it returns a
  cleanup. An effect that sets state from other component values is a bug.
- **Server state** lives in the query cache, never copied into local state.
  **UI state** (draft input, timer, open dialog) is local to the component.
- No global store while one remote source of truth suffices.
- No memoisation, lazy loading, preload or bundle splitting without a measured
  slowdown.

## API

- Types come from the schema **generated** from the backend's published
  contract against the running API. Never hand-written, never edited, kept out
  of the formatter so a reformat cannot hide a real contract change.
- A missing field means the backend contract changed: regenerate, then let the
  compiler list the front code that no longer holds.
- The endpoints module is the only caller of `request()`, and it is
  package-private: a feature reaches the server through queries or not at all.

## Styles

- Design-system components over raw markup: they carry the accessibility.
- Never guess a component's props. Read its documentation from the front root.
- No hard-coded colour, font size or spacing. Tokens only, applied through a
  typed theme definition so an invented token fails to compile. A one-off style
  is a scoped stylesheet next to the component.
- Quality floor on every screen: responsive to mobile, visible keyboard focus,
  reduced-motion respected, button labels that say what they do.

## The toolchain, by role

- **Compiler in strict mode**, plus unchecked index access, exact optional
  properties, unused locals and parameters, fall-through in `switch`.
- **Linter and formatter in one**, recommended presets for the framework,
  project and types domains, warnings promoted to errors. Cognitive complexity
  cap 15, file length cap 300, floating promises forbidden.
- **Import boundaries** as linter overrides, one per feature and one for `ui/`.
- **Test runner** in a browser-like environment, with a network mock for the
  backend.
- **Contract generator** pinned and run in isolation: it must not enter the
  dependency tree.
- **Pre-commit and CI run the same commands**, always from the front root.

Every command from the front root. Elsewhere, config paths resolve from the
wrong directory, and the package runner silently fetches a public namesake
instead of the local binary.

## Tests

- Mock only the network: the backend, at the request level. Never a hook to
  test the component that uses it.
- Enter at the screen. Assert what the user sees: a status, a rendered text,
  the next screen after a click. Never a prop, never an exact sentence.
- No extra test dependency. A test dependency is a dependency.
- A double refuses what the real thing refuses. A lenient fake is a
  tautological test in disguise.
- What the test environment lacks goes in one setup file. A third-party
  component mounted for the first time is run while watching the output, not
  only the counter.
- One smoke test mounts the whole app: providers and routes are wired.
- Break the behaviour, watch the test go red, then fix.

## Before handing back

Type check, lint, tests. From the front root. Zero warnings or it is not done.

## Never

- A dependency without asking. A test dependency is a dependency.
- An abstraction with one caller. Extract on the second real use.
- A feature importing another feature, or `ui/` importing a domain.
- A hand-written type for something the backend already describes.
- An effect that mirrors state.
- A disabled lint rule to get through. Fix the code or settle the rule.
- A comment explaining a decision. Comments mark only the line that looks
  useless and is not, or a coupling invisible from the file.
