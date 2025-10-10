# Flow SDK Test Suite

This document mirrors the simplified test strategy. For the authoritative guide, see `tests/README.md`.

## Organization

```
tests/
├── fast/          # Unit tests (<1s, mocked boundaries only)
├── slow/          # Integration/E2E (real components, minimal mocks)
└── support/       # Fixtures, builders, doubles, scripts
```

## Running

```bash
pytest tests/fast -v            # fast unit tests
pytest tests/slow -v            # integration/E2E
pytest -m "not slow"           # marker-based selection
```

## Best practices
- Mock only at boundaries (HTTP, filesystem) in `fast/`
- Prefer realistic doubles over deep stubs in `slow/`
- Use `tests/support/framework` builders/helpers for clarity
- Keep tests isolated from environment (see `conftest.py`)

Refer to `tests/README.md` for detailed guidance and examples.