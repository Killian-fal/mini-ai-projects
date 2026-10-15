# Frontend

The rules are in `guideline/frontend.md`: read it before writing code. This file only lists
what the code and the guideline do not show, each point verified by hand.

## Commands

Run every command from `frontend/`: `pnpm typecheck`, `pnpm lint`, `pnpm test`, `pnpm format`,
`pnpm gen:api` (needs the API on `http://localhost:5002`). Run `pnpm format` before `pnpm lint`,
which fails on formatting.

## Do not change these

- **No `@/` import alias, relative imports only.** Biome does not resolve tsconfig `paths`: an
  aliased import of a `/** @package */` symbol passes `noPrivateImports`, while the same import
  written relatively is refused. An alias would silently turn the boundary rule into decoration.
- **`/** @package */` is written by hand on each internal export.** Do not set
  `defaultVisibility: "package"` in `biome.json`: Biome evaluates it with the config of the
  importing file, so an override on `features/**` protects nothing against an import from `app/`.
- **The theme lives in `src/ui/theme/`, not in `app/`.** Features and `ui/` need the tokens, and
  nothing may import `app/`.

## Verified pitfalls

- Biome's type inference does not resolve `Exclude<…>`: a `switch` over an excluded union fails
  `useExhaustiveSwitchCases`. Name the sub-union instead (see `OpenComposerState`).
- `useExhaustiveDependencies` reports a dependency the effect does not read. Make the effect use
  what it reacts to (see `useFollowBottom`) rather than relaxing the rule.
- MSW 3 renamed `onUnhandledRequest` to `onUnhandledFrame`. With the old name an unhandled request
  only warns, and the fake server stops being strict.
- An entrance keyframe must not set the final `opacity`: with `animation-fill-mode: both` it
  overrides the component's own opacity (dimmed options, failed card) once the animation ends.
- A mutation's `onError` is awaited before the mutation turns to error: after a 409, the
  conversation is already reloaded when the error becomes visible.
