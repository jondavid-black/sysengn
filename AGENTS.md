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

## 6. YASL (YAML Advanced Schema Language) Guidelines

This project uses YASL for data validation and schema definition. When working with YAML files in this repository, adhere to the following rules and structures.

### 1. Schema Structure

All YASL schemas must be valid YAML files (`.yasl` extension recommended) with a root `definitions` key.

#### Basic Skeleton
```yaml
definitions:
  <namespace>:          # Logical grouping (e.g., 'common', 'config', 'app')
    types:              # Define data models here
      <TypeName>:
        description: "Optional description of the type"
        properties:
          <property_name>:
            type: <primitive_type>
            presence: required  # optional (default), required, preferred
        validators:
          at_least_one: [<property_name>, property_name]
            # ... additional validators
    enums:              # Define reusable value sets here
      <EnumName>:
        values:
          - value1
          - value2
```

#### Namespaces
*   Use namespaces to avoid naming collisions.
*   Refer to types in the same namespace by name: `type: User`.
*   Refer to types in other namespaces by dot notation: `type: common.Address`.

### 2. Supported Primitives

YASL supports a rich set of primitives. **You must use these exact type names.**

#### Standard Types
*   `str` / `string`: Text.
*   `int`: Integer.
*   `float`: Floating-point number.
*   `bool`: Boolean (`true`/`false`).
*   `any`: Any valid YAML value.

#### Time & Date
*   `date`: ISO 8601 Date (`YYYY-MM-DD`).
*   `datetime`: ISO 8601 DateTime (`YYYY-MM-DDTHH:MM:SS`).
*   `clocktime`: Time of day (`HH:MM:SS`).

#### Filesystem & Network
*   `path`: A file system path.
*   `url`: A web URL.

#### Collections
*   `<Type>[]`: A list of items (e.g., `str[]`, `int[]`, `common.Address[]`).
*   `map[<KeyType>, <ValueType>]`: A dictionary. Keys must be `str`, `int`, or an Enum. (e.g., `map[str, int]`).

#### References
*   `ref[<Type>]`: A reference to another object defined elsewhere in the data. The referenced object must have a property marked with `unique: true`.
    *   Example: `owner: { type: ref[User] }` matches a User's unique identifier.

#### Physical Quantities (SI Units)
YASL parses strings with units into physical quantities.
*   `length` (e.g., "10 m", "5 km")
*   `mass` (e.g., "5 kg", "100 g")
*   `time` (e.g., "10 s", "2 min") - *Physical duration, distinct from `clocktime`.*
*   `velocity` (e.g., "10 m/s", "100 km/h")
*   `temperature` (e.g., "300 K")
*   `frequency` (e.g., "60 Hz")
*   `angle` (e.g., "90 deg", "1 rad")
*   `area` (e.g., "100 m2")
*   `volume` (e.g., "10 liters", "5 m3")
*   `pressure` (e.g., "101 kPa", "1 bar")
*   `energy` (e.g., "100 J", "1 kWh")
*   `power` (e.g., "100 W")
*   `voltage` / `electrical potential` (e.g., "12 V")
*   `current` / `electrical current` (e.g., "10 A")
*   `resistance` / `electrical resistance` (e.g., "50 ohm")
*   `data quantity` (e.g., 8 byte, 50 Gb)

### 3. Validation Rules

Apply these validators as keys under the property definition.

#### General Validators
*   `presence`:
    *   `optional` (default): Field can be omitted.
    *   `required`: Field must exist.
    *   `preferred`: Warns if missing, but valid.
*   `unique`: `true` enforces global uniqueness for this property value across the dataset.
*   `default`: Provides a default value if missing.

#### Numeric & Physical Validators
Applies to `int`, `float`, and physical types. **Physical validators automatically handle unit conversion.**
*   `gt`: Greater than (`>`). (e.g., `gt: 10 m` allows "11 m" and "1 km", rejects "5 m").
*   `ge`: Greater than or equal to (`>=`).
*   `lt`: Less than (`<`).
*   `le`: Less than or equal to (`<=`).
*   `multiple_of`: Value is a multiple of X. (e.g., `multiple_of: 0.5`).
*   `exclude`: List of forbidden values.

#### String Validators
Applies to `str`.
*   `str_min`: Min length (int).
*   `str_max`: Max length (int).
*   `str_regex`: Regex pattern string.

#### Path/File Validators
Applies to `path` and `str`.
*   `path_exists`: `true` checks if path exists on disk.
*   `is_file`: `true` ensures it's a file.
*   `is_dir`: `true` ensures it's a directory.
*   `file_ext`: List of allowed extensions (e.g., `['.py', '.txt']`).

#### URL Validators
Applies to `url` and `str`.
*   `url_protocols`: List of allowed schemes (e.g., `['https']`).
*   `url_reachable`: `true` attempts a network request to verify reachability.

#### Type-Level Validators
Defined at the `Type` level within 'validators' (sibling to `properties`).
*   `only_one`: List of fields; exactly one must be present.
*   `at_least_one`: List of fields; one or more must be present.
*   `if_then`:
    ```yaml
    if_then:
      - eval: status           # Check this field
        value: [active]        # If equal to 'active'
        present: [start_date]  # Then 'start_date' must exist
        absent: [reason]       # And 'reason' must NOT exist
    ```

### 4. CLI Workflow

Use the CLI to verify your schemas and data.

1.  **Check Schema Syntax**:
    ```bash
    uv run yasl schema <path/to/schema.yasl>
    ```

2.  **Validate Data against Schema**:
    ```bash
    uv run yasl check <path/to/schema.yasl> <path/to/data.yaml>
    ```

### 5. Comprehensive Example

```yaml
definitions:
  config:
    types:
      ServerConfig:
        description: Main configuration for the server
        properties:
          host_ipv4:
            type: str
            str_regex: ^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$
          host_ipv6:
            type: str
          port:
            type: int
            gt: 1024
            lt: 65535
            default: 8080
          max_upload_size:
            type: data quantity
            le: 50 mb
            description: Max file upload size
          timeout:
            type: time
            default: 30 s
          environment:
            type: EnvEnum
            presence: required
        validators:
          at_least_one: [host_ipv4, host_ipv6]

    enums:
      EnvEnum:
        values: [dev, stage, prod]
```

## 7. Agent Behavior Rules

1. **Verify First:** Before editing, read the file and run `grep` to find usages.
2. **Incremental Changes:** Do not refactor unrelated code unless requested.
3. **Safety:** Never hardcode credentials. Use environment variables.
4. **Self-Correction:** If a build/test fails, analyze the error output, hypothesize a fix, and retry.
5. **Cleanliness:** Remove debug print statements before finishing a task. Use the `logging` module instead.

---
*End of Guidelines*
