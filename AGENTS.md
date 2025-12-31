# SysEngn Agent Guidelines

This document provides essential context, commands, and conventions for AI agents (and humans) working on the SysEngn repository.

## 1. Project Overview

SysEngn (System Engine) is an integrated platform combining project management, systems engineering, collaboration, document management, and UX design.
**The application is built using [Flet](https://flet.dev/) for the user interface.**

- **Stack:** Python 3.12+
- **UI Framework:** Flet
- **Dependency Manager:** `uv` (Exclusive)
- **Linter/Formatter:** `ruff`
- **Type Checker:** `pyright`
- **Testing:** `pytest`
- **Documentation:** `mkdocs`

## 2. Environment & Commands

The project uses `pyproject.toml` for configuration. Always use `uv` for dependency management and running commands.

### Setup
```bash
# Install dependencies
uv sync
```

### Verification & Quality Control
Run these commands before submitting any changes.

```bash
# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/sysengn/test_main.py

# Run a specific test case (CRITICAL for focused development)
uv run pytest tests/sysengn/test_main.py::test_initialization

# Linting (fixable errors)
uv run ruff check . --fix

# Formatting
uv run ruff format .

# Type Checking
uv run pyright .
```

## 3. Code Style & Conventions

Adhere strictly to these rules to maintain codebase consistency.

### 3.1 Python Version & Features
- Target **Python 3.12+**.
- Use modern typing syntax (e.g., `list[str]` instead of `List[str]`, `str | None` instead of `Optional[str]`).
- Specific imports are preferred over `*`.

### 3.2 Imports
- Absolute imports are preferred for clarity (e.g., `from sysengn.auth import User`).
- Group imports: standard library, third-party, local application (Ruff handles this).
- Avoid circular imports by using `TYPE_CHECKING` blocks for type-only dependencies.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sysengn.models import Project
```

### 3.3 Typing
- **Strict Typing:** All function signatures (params and return types) MUST have type hints.
- Use `Any` sparingly. Prefer specific types or Generics.
- Use `Protocol` for structural typing when interfaces are needed but inheritance is not strict.

### 3.4 Formatting & Naming
- **Line Length:** Follow Ruff defaults (typically 88 chars).
- **Naming:**
    - Classes: `PascalCase`
    - Functions/Variables: `snake_case`
    - Constants: `SCREAMING_SNAKE_CASE`
    - Private members: `_leading_underscore`
- **Docstrings:** Use **Google Style** docstrings for all public modules, classes, and functions.

```python
def process_data(data: dict[str, Any], schema_version: int = 1) -> bool:
    """Processes the input data against the system schema.

    Args:
        data: A dictionary containing the raw system data.
        schema_version: The version of the schema to validate against.

    Returns:
        True if processing succeeds, False otherwise.

    Raises:
        ValidationError: If the data structure is invalid.
    """
    ...
```

### 3.5 Error Handling
- Use specific, custom exceptions defined in a `exceptions.py` module within the relevant package.
- Avoid bare `except:` or generic `except Exception:`. catch specific errors.
- Errors should be descriptive and provide context.

```python
# Good
class ConfigurationError(Exception):
    """Raised when system configuration is invalid."""

try:
    load_config()
except FileNotFoundError as e:
    raise ConfigurationError(f"Config file missing: {e}") from e
```

### 3.6 File Structure
- Source code resides in `src/sysengn`.
- Tests mirror the source structure in `tests/`.
- `__init__.py` files should expose the public API of a package, keeping implementation details internal.

## 4. Testing Guidelines

- **Unit Tests:** Focus on isolating logic. Mock external dependencies (filesystem, network, database).
- **Fixtures:** Use `conftest.py` for shared fixtures (e.g., sample project data, temporary directories).
- **Coverage:** Aim for high coverage on core logic.
- **Async:** If testing async code, use `pytest-asyncio`.

```python
# tests/sysengn/test_project_manager.py
import pytest
from sysengn.project_manager import ProjectManager

@pytest.fixture
def empty_manager():
    return ProjectManager()

def test_add_project(empty_manager):
    proj_id = empty_manager.create_project("New App", "Description")
    assert proj_id is not None
    assert empty_manager.get_project(proj_id).name == "New App"
```

## 5. Flet UI Guidelines

- **Components:** Break complex UIs into smaller, reusable `ft.UserControl` or functional components.
- **State:** Manage state carefully. Use `page.session` for user session data.
- **Responsiveness:** Use `ft.Row`, `ft.Column`, and `expand=True` to create responsive layouts.
- **Theming:** Respect `page.theme_mode`. Use standard colors (e.g., `ft.Colors.BLUE`, `ft.Colors.GREY_800`) to ensure dark/light mode compatibility.

## 6. Agent Behavior Rules

1. **Verify First:** Before editing, read the file and run `grep` to find usages.
2. **Incremental Changes:** Do not refactor unrelated code unless requested.
3. **Safety:** Never hardcode credentials. Use environment variables.
4. **Self-Correction:** If a build/test fails, analyze the error output, hypothesize a fix, and retry.
5. **Cleanliness:** Remove debug print statements before finishing a task. Use the `logging` module instead.

---
*End of Guidelines*
