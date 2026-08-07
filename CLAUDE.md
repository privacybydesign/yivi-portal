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
  carry `libc` arrays). An older npm silently drops those fields on any lockfile *write*, so
  use a matching major for anything that rewrites it: `npx -y npm@12 install`. `npm ci` only
  reads the lockfile, so CI running plain `npm ci` on node 22 (npm 10.9.x) is fine.
- npm 12 refuses `remote`-type tarballs by default and dies with `EALLOWREMOTE` on
  `@tailwindcss/oxide-wasm32-wasi` before it writes anything. Pass `--allow-remote=all`.
- Any npm 11+ write also adds six `@tailwindcss/oxide-wasm32-wasi/node_modules/*` entries the
  current lockfile is missing (`inBundle: true`, `optional: true`, wasm32-wasi only, so never
  installed here). Expect them in the diff of an otherwise unrelated bump.
- Entries in the `overrides` block need an upper bound. An override *replaces* the dependent's
  own range, so a bare `">=x"` lets a fresh resolve pick the next major — `js-yaml` is pinned
  `">=4.3.1 <5"` because `@eslint/eslintrc` asks for `^4.1.0` and js-yaml 5 exists.

## portal_backend

- `poetry install` with no flags tries to build `uwsgi` from source (it is in the non-optional
  `prod` group) and fails without Python headers. Use `poetry install --without prod` for
  local work; the Docker images pass the group they need.
- `manage.py` picks the settings module from `$ENVIRONMENT`, and `.env.testing` sets
  `ENVIRONMENT=development`, so `manage.py test` runs under `yivi_portal/settings/development.py`.
  Anything the development settings import has to be installed in `Dockerfile.django` too,
  which happens to hold because `poetry install --with prod` also installs the `dev` group.
- Two tests in `portal_backend/tests/test_imports.py` read `/app/config.json`, the path the
  config lands on inside the container. They pass in CI and error out on a checkout run
  outside Docker; that is the environment, not the code.
- `test_add_maintainer_created` needs `YIVI_PORTAL_URL` set, otherwise the invite mail blows
  up and the view answers 500. Note that `.env.testing` writes it as `YIVI_PORTAL_URL= portal.yivi.app`
  with a leading space: `docker run --env-file` keeps the space and the test passes, but
  `set -a; . ./.env.testing` in a shell parses the line as a command and never exports the
  variable at all, so a local run fails a test CI does not.
- django-silk is development-only: the app, its middleware and its `/silk/` route are added in
  `settings/development.py` and guarded in `yivi_portal/urls.py` by an `INSTALLED_APPS` check.
  Keep it out of `settings/base.py`; silk records request and response bodies and serves an
  unauthenticated dashboard.
- Poetry 2.x `poetry lock` keeps whatever the lockfile already resolved as long as it still
  satisfies `pyproject.toml`, and `poetry update <pkg> --lock` walks to the newest release the
  manifest range allows — with `django = "^6.0"` that is the next *minor*, not the security
  patch. To land a patch without changing the manifest: narrow the constraint temporarily
  (`~6.0.6`), `poetry update django --lock`, restore the constraint, `poetry lock` again. The
  second lock recomputes the content hash off the restored manifest and leaves the version
  alone, so the diff stays at the one package and `poetry check --lock` passes.
- `pip-audit` reads requirements, not `poetry.lock`. Flatten it first:
  `python3 -c "import tomllib;[print(f\"{p['name']}=={p['version']}\") for p in tomllib.load(open('poetry.lock','rb'))['package']]" > /tmp/reqs.txt && pip-audit -r /tmp/reqs.txt --no-deps`

## CI

- `.github/workflows/react-container.yml` runs `npm run test` in `portal_spa/`, then builds
  `Dockerfile.react`. The image is only pushed outside pull requests and scheduled runs.
- `.github/workflows/django-container.yml` and `ruff-linter.yml` cover the backend; they use
  `paths-ignore: portal_spa/**`, which skips the run only when *every* changed file is under
  `portal_spa/**`. A pull request touching both halves runs both — this one does, which is
  why it shows four checks.
- `react-container.yml` filters the other way round (`paths: portal_spa/**` plus
  `.github/workflows/react-*.yml`), so a change touching neither of those gets no React run
  at all.
- `ruff-linter.yml` runs `pip install ruff` unpinned, so the linter can change under the
  repo. The rule set lives in `[tool.ruff.lint]` in `pyproject.toml` instead, which keeps
  `ruff check .` deterministic across ruff releases.
