# Notes for working on yivi-portal

Django backend in `portal_backend/` + `yivi_portal/`, React SPA in `portal_spa/`.

## portal_spa

- `npm run build` is `tsc -b && vite build`, so a type error fails the build. `npm test`
  type-checks first (`pretest` -> `typecheck`), so type errors surface in the `run-tests`
  job instead of only in the slower Docker build.
- `vite.config.ts` imports `defineConfig` from `vitest/config`, not from `vite`. The `test`
  block is only typed there; vitest 4 no longer widens Vite's config type through
  `/// <reference types="vitest" />`, so importing from `vite` breaks `tsc -b`.
- Tests live in `portal_spa/tests` (vitest `dir: 'tests'`, jsdom, `globals: true`), separate
  from `src`. Both are in the `tsconfig.app.json` project; `vite.config.ts` is in
  `tsconfig.node.json`.
- `package-lock.json` was written by npm 11+ (the optional `@img/sharp-*` platform packages
  carry `libc` arrays). An older npm silently drops those fields on any lockfile write, so
  use a matching major: `npx -y npm@12 ci` / `npx -y npm@12 install`.

## CI

- `.github/workflows/react-container.yml` runs `npm run test` in `portal_spa/`, then builds
  `Dockerfile.react`. The image is only pushed outside pull requests and scheduled runs.
- `.github/workflows/django-container.yml` and `ruff-linter.yml` cover the backend; they use
  `paths-ignore: portal_spa/**`, so the two halves never both run on one pull request.
- A change outside `portal_spa/**` therefore gets no React run at all.
- `ruff-linter.yml` runs `pip install ruff` unpinned, so the linter can change under the
  repo. The rule set lives in `[tool.ruff.lint]` in `pyproject.toml` instead, which keeps
  `ruff check .` deterministic across ruff releases.
