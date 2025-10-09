# Changelog

## 0.1.0 - 2025-02-14

- First public release on PyPI under the name `spaps`.
- Adds synchronous and asynchronous clients mirroring the TypeScript SDK, including
  sessions, payments (crypto included), usage, whitelist, secure messages, and metrics helpers.
- Provides configurable retry/backoff handling, structured logging hooks, and token storage
  abstractions (in-memory & file-backed).
- Ships lint (`ruff`), type checking (`mypy`), coverage enforcement, and integration smoke
  tests wired into the release workflow.
- Updates documentation with Python quickstart examples and a dedicated backend guide.
