# Development notes

Things about building and testing this repository that are not obvious from the
code, and that cost time when you find them the hard way. Setup and day-to-day
commands are in the [README](../README.md); this file is the small print under it.

## Frontend (`portal_spa`)

- `npm run build` is `tsc -b && vite build`, so a type error fails the build.
  `npm test` type-checks first (`pretest` -> `typecheck`), which surfaces type
  errors in the `frontend` job instead of only in the slower Docker build.
- `vite.config.ts` imports `defineConfig` from `vitest/config`, not from `vite`.
  The `test` block is only typed there: vitest 4 no longer widens Vite's config
  type through `/// <reference types="vitest" />`, so importing from `vite` breaks
  `tsc -b`.
- Tests live in `portal_spa/tests` (vitest `dir: 'tests'`, jsdom, `globals: true`),
  separate from `src`. Both are in the `tsconfig.app.json` project;
  `vite.config.ts` is in `tsconfig.node.json`.
- `package-lock.json` was written by npm 11 or newer — the optional
  `@img/sharp-*` platform packages carry `libc` arrays. An older npm silently drops
  those fields on any lockfile *write*, so use a matching major for anything that
  rewrites it: `npx -y npm@12 install`. `npm ci` only reads the lockfile, so CI
  running plain `npm ci` on node 22 (npm 10.9.x) is fine.

## Backend (`portal_backend`)

- `poetry install` with no flags tries to build `uwsgi` from source (it is in the
  non-optional `prod` group) and fails without Python headers. Use
  `poetry install --without prod` for local work; the Docker images pass the group
  they need.
- `manage.py` picks the settings module from `$ENVIRONMENT`, and `.env.testing`
  sets `ENVIRONMENT=development`, so `manage.py test` runs under
  `yivi_portal/settings/development.py`. Anything the development settings import
  has to be installed in `Dockerfile.django` too, which happens to hold because
  `poetry install --with prod` also installs the `dev` group.
- Two tests in `portal_backend/tests/test_imports.py` read `/app/config.json`, the
  path the config lands on inside the container. They pass in CI and error out on a
  checkout run outside Docker; that is the environment, not the code.
- `portal_backend/tests/test_claude_md_orientation.py` reads `CLAUDE.md` from the
  repository root and the suite runs *inside* the image, so `CLAUDE.md` has to stay
  out of `.dockerignore` — which already excludes `README.md`, a file of the same
  kind. Adding it, or a `*.md` pattern, errors both tests with `FileNotFoundError`
  in CI rather than skipping them.
- `test_add_maintainer_created` needs `YIVI_PORTAL_URL` set, otherwise the invite
  mail blows up and the view answers 500. Note that `.env.testing` writes it as
  `YIVI_PORTAL_URL= portal.yivi.app` with a leading space: `docker run --env-file`
  keeps the space and the test passes, but `set -a; . ./.env.testing` in a shell
  parses the line as a command and never exports the variable at all, so a local
  run fails a test CI does not.
- django-silk is development-only, and the guard is in two places: the app, its
  middleware and its `/silk/` route are added in `settings/development.py`, and
  `yivi_portal/urls.py` only registers the route behind an `INSTALLED_APPS` check.
  Keep it out of `settings/base.py` — silk records request and response bodies,
  including `Authorization` headers, and its dashboard has no access control of its
  own. See the README's query profiling section for how to use it.

## CI

CI uses the shared workflows from `privacybydesign/github-workflows`; the
callers are in `.github/workflows/`.

- `status-checks.yml` runs on every pull request, with no path filters:
  `frontend` (`npm run lint`, `test`, `build` in `portal_spa/`), `ruff`,
  `django-tests` (builds `Dockerfile.django` and runs `manage.py test` inside
  it), a build and scan of both images without pushing them, dependency review
  and workflow lint. `Status checks passed` is the one check to require.
- `delivery.yml` pushes `ghcr.io/privacybydesign/django-portal` and
  `ghcr.io/privacybydesign/react-portal`: `:edge` from `main`, `:X.Y.Z` and
  `:latest` from a release. Both images are built on every push, whichever half
  changed.
- `image-rescan.yml` re-scans the published `:edge` and latest-release images
  every Monday.
- The `ruff` job runs `pip install ruff` unpinned, so the linter can change
  under the repo. The rule set lives in `[tool.ruff.lint]` in `pyproject.toml`
  instead, which keeps `ruff check .` deterministic across ruff releases.

## Admin login

- The Django admin asks for a Yivi disclosure of the account's email after the
  password (`yivi_portal/admin_site.py`). The widget it uses,
  `portal_backend/static/admin_yivi/yivi.js`, is the checked-in browser bundle of
  `@privacybydesign/yivi-frontend` 1.0.4, so the admin runs no third-party
  script. After bumping that package in `portal_spa`, copy its
  `dist/yivi.js` over it.
