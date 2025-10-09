# Python Client TODO

## Milestone 0 – Scaffolding
- [x] Confirm packaging backend choice (`hatchling`) and document rationale
- [x] Add initial failing metadata tests (`pyproject` presence, `__version__` export)
- [x] Implement minimal scaffolding to satisfy metadata tests (pyproject, version module)

## Milestone 1 – Auth Token Lifecycle
- [x] Design response models for nonce/token flows (pydantic)
- [x] Add failing auth tests (`request_nonce`, `verify_wallet`, `refresh_tokens`)
- [x] Implement auth client to satisfy tests using `httpx`
- [x] Document Python auth flow examples in `docs/api/wallet-authentication.md`

## Milestone 2 – Session Validation
- [x] Add failing session validation tests (`validate`, `current`)
- [x] Implement sessions module with structured responses
- [x] Update Sessions docs and manifest entries with Python references

## Milestone 3 – Configuration & Environment
- [x] Add failing config tests (env defaults, timeouts, retries)
- [x] Implement configuration module and HTTP client abstraction
- [x] Extend `.env.example` tips + add new Python backend doc

## Milestone 4 – Packaging & Distribution
- [x] Add build/install integration tests (`python -m build`, temp venv)
- [x] Finalize metadata (classifiers, dependencies, extras)
- [x] Draft release checklist in docs

## Milestone 5 – Payments & Usage
- [x] Identify priority routes (Stripe checkout, balance, usage reporting)
- [x] Add failing tests for `PaymentsClient.create_checkout_session`
- [x] Add failing tests for balance/usage endpoints
- [x] Implement payments client with models & error handling
- [x] Update payments docs/manifest with Python references

## Ongoing
- [ ] Keep changelog up to date (`packages/python-client/CHANGELOG.md`)
- [ ] Wire pytest command into repo scripts/CI
- [ ] Align SDK and Python docs for every new feature
