import pytest
import subprocess
import os

# Constants
SCHEMA_PATH = "src/sysengn/data/schemas/sysmlv2.yasl"
DATA_PATH = "tests/sysengn/data/sysml_test_data.yaml"


def test_validate_sysml_data_cli():
    """
    Verify that the SysML v2 example data is valid according to the schema
    by invoking the YASL CLI tool.
    """

    # 1. Ensure files exist
    assert os.path.exists(SCHEMA_PATH), f"Schema not found at {SCHEMA_PATH}"
    assert os.path.exists(DATA_PATH), f"Test data not found at {DATA_PATH}"

    # 2. Construct command
    # uv run yasl check <schema> <data>
    command = ["uv", "run", "yasl", "check", SCHEMA_PATH, DATA_PATH]

    # 3. Execute command
    result = subprocess.run(command, capture_output=True, text=True)

    # 4. Verify Success
    # If the schema is valid and data conforms, exit code should be 0
    if result.returncode != 0:
        pytest.fail(
            f"YASL validation failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )


if __name__ == "__main__":
    test_validate_sysml_data_cli()
