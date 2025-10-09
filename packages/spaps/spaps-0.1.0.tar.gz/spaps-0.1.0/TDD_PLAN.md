# Sweet Potato Python Client – TDD Plan

## Objectives
- Deliver a first-party Python package that mirrors the developer experience of the JavaScript `spaps-sdk`, optimized for backend/server use.
- Ship production-ready wheels (PyPI-compatible) with type hints, deterministic tests, and docs that stay aligned with SPAPS API changes.
- Follow SPAPS workflow: tests first, minimal implementation, docs/manifest updates.

## Target Package Layout
```
packages/python-client/
├── pyproject.toml            # Build metadata (PEP 621), poetry/pdm backend TBD
├── README.md                 # Usage, examples, API docs
├── src/
│   └── spaps_client/
│       ├── __init__.py
│       ├── config.py         # Env + settings management
│       ├── http.py           # HTTP client abstraction (requests/httpx)
│       ├── auth.py           # Token lifecycle helpers
│       ├── sessions.py       # Session validation helpers
│       ├── payments/         # Future Stripe/crypto modules
│       └── errors.py         # Rich exceptions mapped from SPAPS error payloads
├── tests/
│   ├── conftest.py
│   ├── fixtures/             # Shared mocks (responses/httpx respx)
│   ├── unit/
│   └── integration/
└── docs/
    └── python-client.md      # Mirrors JS SDK quickstart, with “Related Internals”
```

## Tooling Decisions (to validate with TDD)
- **HTTP**: `httpx` (sync + async) for flexible usage. Mock with `respx`.
- **Serialization**: `pydantic` models for typed responses & validation.
- **Testing**: `pytest` with `pytest-asyncio`, `respx`, and `pytest-cov`.
- **Packaging**: `pyproject.toml` + `hatchling` (lightweight) or `poetry` backend.
- **CI hooks**: ensure compatibility with existing npm scripts (`npm run verify:deps`, `npm run docs:validate-all`).

## Milestones & TDD Steps

### Milestone 0 – Scaffolding Tests
1. Write failing tests asserting package metadata exists (`pyproject.toml`, version exposed in `spaps_client.__version__`).
2. Add failing doc-validation test ensuring README code snippets compile (use doctest/pytest).

### Milestone 1 – Auth Token Lifecycle
- **Tests first**:
  - `tests/unit/test_auth_nonce.py`: expects `AuthClient.request_nonce` to POST `/api/auth/nonce` with API key headers and return nonce/message/expiry.
  - `tests/unit/test_auth_verify.py`: ensures `verify_wallet` sends signature payload, handles success/failure, raises custom exceptions on 4xx/5xx.
  - `tests/unit/test_auth_refresh.py`: covers refresh flow and token storage abstraction.
  - Mock HTTP responses via `respx` fixtures; assert request payloads match SPAPS API schemas (see `src/routes/auth.ts` & `docs/api/wallet-authentication.md`).
- **Implementation**: minimal code to satisfy tests; introduce data models (`NonceResponse`, `TokenPair`).
- **Docs**: update `docs/api/wallet-authentication.md` “Related Internals” with Python package reference once tests pass.

### Milestone 2 – Session Validation
- Tests:
  - `tests/unit/test_sessions_validate.py`: `SessionsClient.validate()` hitting `/api/sessions/validate`; returns structured session metadata.
  - `tests/unit/test_sessions_current.py`: ensures caching of current session call and error translation.
  - Negative tests for expired/invalid JWT (anticipate `401` with `INVALID_SESSION` code).
- Implementation: add module sto stub for session operations.
- Docs: extend `docs/api/sessions.md` with Python snippets; update `docs/manifest.json` entries for `/api/sessions/*` to include new tests.

### Milestone 3 – Configuration & Environment
- Tests:
  - `tests/unit/test_config.py`: default API URL/key from env (`SPAPS_API_URL`, `SPAPS_API_KEY`), fallback to local defaults.
  - `tests/unit/test_http_client.py`: HTTP timeout, retry/backoff configuration.
- Implementation: config objects, HTTP wrapper (sync), optional async variant (guarded by extra dependency `httpx[http2]`).
- Docs: add Python-specific environment guidance to `.env.example` (commented) & new doc page `docs/guides/python-backend.md`.

### Milestone 4 – Packaging & Distribution
- Tests:
  - `tests/integration/test_build.py`: invokes `python -m build` (or backend equivalent) and asserts wheel/sdist produced in `dist/`.
  - `tests/integration/test_installation.py`: installs built wheel into temp venv to ensure imports succeed.
- Implementation: finalize `pyproject.toml`, include license classifiers, add `__version__`.
- Docs: README badges, release checklist in `docs/AGENTS_CC.md`.

### Milestone 5 – Optional Features
- Payments (Stripe, crypto), admin methods, usage tracking—mirror JavaScript SDK priorities. Each feature enters with:
  - Route-level tests hitting recorded JSON fixtures.
  - Error regression tests (403, rate limits).
  - Docs updates (API refs + manifest).

## Testing Strategy
- Run targeted suites via `pytest tests/unit` within package.
- Add npm script wrapper (`"test:python-client": "cd packages/python-client && pytest -q"` ) so CI integrates seamlessly.
- Ensure no live network calls: respx strictly intercepts HTTPX; add guard test (`respx.assert_all_called()`).
- For crypto/webhook features, snapshot expected request bodies (JSON fixtures under `tests/fixtures`).

## Documentation & Manifest Updates
- When features land, update:
  - `docs/manifest.json`: add Python client tests under relevant endpoints.
  - `docs/api/*`: include “Python Backend Example” sections.
  - `SDK_QUICKSTART.md`: cross-link to new Python Quickstart.
- Maintain changelog (`packages/python-client/CHANGELOG.md`) aligned with releases.

## Outstanding Questions / Follow-ups
1. Packaging backend: prefer `hatchling` (minimal) vs `poetry`? Decide before Milestone 0 tests.
2. Async support: ship in v0.1 or defer?
3. Token storage interface: simple return dict vs pluggable storage (Redis, DB). Align with backend needs.
4. Release automation: integrate with existing release scripts (`scripts/`) or add GitHub workflow?

## Next Steps
1. Confirm tooling choices (httpx, hatchling) with project maintainers.
2. Create initial test scaffolding (Milestone 0) and fail CI intentionally to drive implementation.
3. Schedule documentation tasks to coincide with feature milestones so manifest stays accurate.
