# SysEngn Agent Guidelines

This document provides essential context, commands, and conventions for AI agents (and humans) working on the SysEngn repository.

## 1. Project Overview

SysEngn (System Engine) is an integrated platform combining project management, systems engineering, collaboration, document management, and UX design.

- **Stack:** Python 3.12+
- **Dependency Manager:** `uv` (preferred) or `pip`
- **Linter/Formatter:** `ruff`
- **Type Checker:** `pyright`
- **Testing:** `pytest`
- **Documentation:** `mkdocs`

## 2. Environment & Commands

The project uses `pyproject.toml` for configuration.

### Setup
```bash
# Install dependencies using uv (fastest)
uv sync

# OR using pip
pip install -e ".[dev]"
```

### Verification & Quality Control
Run these commands before submitting any changes.

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_core.py

# Run a specific test case (CRITICAL for focused development)
pytest tests/test_core.py::test_initialization

# Linting (fixable errors)
ruff check . --fix

# Formatting
ruff format .

# Type Checking
pyright .
```

## 3. Code Style & Conventions

Adhere strictly to these rules to maintain codebase consistency.

### 3.1 Python Version & Features
- Target **Python 3.12+**.
- Use modern typing syntax (e.g., `list[str]` instead of `List[str]`, `str | None` instead of `Optional[str]`).
- specific imports are preferred over `*`.

### 3.2 Imports
- Absolute imports are preferred for clarity (e.g., `from sysengn.core import System`).
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

- **Unit Tests:** Focus on isolating logic. Mock external dependencies (filesystem, network).
- **Fixtures:** Use `conftest.py` for shared fixtures (e.g., sample project data, temporary directories).
- **Coverage:** Aim for high coverage on core logic.
- **Async:** If testing async code, use `pytest-asyncio`.

```python
# tests/test_manager.py
import pytest
from sysengn.manager import ProjectManager

@pytest.fixture
def empty_manager():
    return ProjectManager()

def test_add_document(empty_manager):
    doc_id = empty_manager.add_document("Design Spec", "content...")
    assert doc_id is not None
    assert empty_manager.get_document(doc_id).title == "Design Spec"
```

## 5. Documentation

- Update `README.md` for high-level changes.
- Ensure docstrings are updated when function signatures change.
- Use Markdown for all documentation files.

## 6. Agent Behavior Rules

1. **Verify First:** Before editing, read the file and run `grep` to find usages.
2. **Incremental Changes:** Do not refactor unrelated code unless requested.
3. **Safety:** Never hardcode credentials. Use environment variables.
4. **Self-Correction:** If a build/test fails, analyze the error output, hypothesize a fix, and retry.
5. **Cleanliness:** Remove debug print statements before finishing a task. Use the `logging` module instead.

---
*End of Guidelines*
