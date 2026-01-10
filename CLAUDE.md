## Project Overview

Web Monitor is a full-stack application that monitors webpages for visual changes. Users add URLs with configurable intervals, Celery workers take screenshots via Playwright, and perceptual hashing detects meaningful visual differences. Only changed screenshots are stored in S3.

Backend: Django + Django Ninja, Celery Beat + Celery, Playwright, PostgreSQL, MinIO (S3).

Frontend: React SPA with TypeScript, Mantine, Tailwind. Bun dev server in development, nginx serves built files in production.

## Code Style

- Fully typed functions
- Pure functions when possible
- Guard clauses; happy path last
- Blank line before returns when preceded by other code
- At least one unit test per function; Use a parameterized test if the function has multiple code paths, with at least one test case per path
- Test naming: `test_<function_name>` for functions, `test_<endpoint>_<method>` for endpoints (e.g., `test_webpage_get`)
- Single quotes
- 100 character line length
- No section comments
- Docstrings under functions, no blank line after:

```python
def process_url(url: str) -> Screenshot:
    """Capture screenshot and compute perceptual hash."""
    if not url:
        raise ValueError('URL required')

    if is_cached(url):
        screenshot = get_from_cache(url)

        return screenshot

    screenshot = capture(url)
    save_to_cache(url, screenshot)

    return screenshot
```

## Commands

- `make test_frontend`: Run frontend tests
- `make test_backend`: Run backend tests
- `make test`: Run all tests
- `make check_frontend`: Run frontend linting and typechecking
- `make check_backend`: Run backend linting and typechecking
- `make check`: Run all checks

Prefer running specific tests over full test suites when possible (e.g., `pytest -k test_name`).
