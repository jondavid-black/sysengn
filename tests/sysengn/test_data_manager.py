import sqlite3
import pytest
from pathlib import Path
from sysengn.db.database import init_db, get_connection
from sysengn.data.manager import DataManager

# --- DB Tests ---


@pytest.fixture
def test_db_path(tmp_path):
    """Fixture to provide a temporary database path."""
    db_file = tmp_path / "test_sysengn.db"
    return db_file


def test_init_db(test_db_path):
    """Test that the database initializes correctly."""
    init_db(test_db_path)
    assert test_db_path.exists()

    conn = get_connection(test_db_path)
    cursor = conn.cursor()

    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    assert cursor.fetchone() is not None

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='projects'"
    )
    assert cursor.fetchone() is not None

    conn.close()


# --- DataManager Tests ---


@pytest.fixture
def controlled_data_setup(tmp_path):
    """Fixture to set up a temporary controlled data environment."""
    root = tmp_path / "controlled_data"
    schemas = root / "schemas"
    schemas.mkdir(parents=True)

    # Corrected ProjectType schema again.
    # The error "Referenced type 'project_mgmt' for property 'project_types' not found" suggests
    # that 'project_mgmt' is interpreted as the type name, not the namespace.
    # 'ref[project_mgmt.ProjectType][]' -> 'ref_target' is 'project_mgmt.ProjectType'
    # The code splits by last dot: ref_type_name='ProjectType', ref_type_namespace='project_mgmt'
    # It tries to find 'ProjectType' in namespace 'project_mgmt'.
    # If the definitions block is:
    # definitions:
    #   project_mgmt:
    #     types:
    #       ProjectType: ...
    # This should work.
    # However, maybe yasl internal registry needs types to be fully registered before referenced.
    # Or maybe the reference needs to point to a *property* of a type if it's using the ReferenceMarker logic?
    #
    # Wait, looking at `gen_pydantic_type_models`:
    # It checks if `ref_target` format is TypeName.PropertyName.
    # "Reference '{ref_target}' ... must be in the format TypeName.PropertyName or Namespace.TypeName.PropertyName"
    #
    # Ah! 'ref[...]` in yasl seems to be for *Foreign Key* style references to values in other data,
    # NOT for defining a nested object structure (composition).
    #
    # For composition (nesting types), we simply use the type name directly as the type of the property.
    # e.g. type: "project_mgmt.ProjectType[]"

    project_type_schema = """
metadata:
  version: "0.1.0"
definitions:
  project_mgmt:
    types:
      ProjectType:
        properties:
          id:
            type: str
            presence: required
          name:
            type: str
            presence: required
          phases:
            type: str[]
            presence: required
      
      ProjectTypesConfig:
        properties:
          project_types:
            # Direct type reference for composition
            type: "project_mgmt.ProjectType[]"
            presence: required
"""
    (schemas / "project_type.yaml").write_text(project_type_schema)

    # Data file needs to match the ProjectTypesConfig structure
    project_types_data = """
project_types:
  - id: "test-eng"
    name: "Test Engineering"
    phases:
      - "Phase 1"
"""
    (root / "project_types.yaml").write_text(project_types_data)

    return root


def test_data_manager_loading(controlled_data_setup):
    """Test loading of controlled data."""
    manager = DataManager(controlled_data_path=controlled_data_setup)
    manager.load_controlled_data()

    data = manager.get_controlled_data("project_types")

    if data is None:
        print("Data failed to load.")

    assert data is not None
    assert len(data) > 0
    first_doc = data[0]
    assert hasattr(first_doc, "project_types")
    assert len(first_doc.project_types) > 0

    project_type = first_doc.project_types[0]
    assert project_type.id == "test-eng"
