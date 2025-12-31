import logging
from pathlib import Path
from typing import Any

from yasl import load_data_files, load_schema_files

logger = logging.getLogger(__name__)

# Define paths
CONTROLLED_DATA_PATH = Path("controlled_data")


class DataManager:
    """
    Manages access to both controlled (YAML/Git) and uncontrolled (SQLite) data.
    """

    def __init__(self, controlled_data_path: Path | None = None):
        self.controlled_path = controlled_data_path or CONTROLLED_DATA_PATH
        self.schemas_path = self.controlled_path / "schemas"
        # Stores loaded data models, keyed by some identifier (e.g., 'project_types')
        self._controlled_data: dict[str, Any] = {}

    def load_controlled_data(self) -> None:
        """Loads schemas and data from the controlled data repository."""
        if not self.controlled_path.exists():
            logger.warning(
                f"Controlled data path {self.controlled_path} does not exist."
            )
            return

        try:
            # 1. Load all schemas from the schemas directory
            if self.schemas_path.exists():
                # yasl supports .yasl and .yaml for schemas usually, but we named ours .yaml
                for schema_file in self.schemas_path.rglob("*.yaml"):
                    logger.info(f"Loading schema: {schema_file}")
                    load_schema_files(str(schema_file))
            else:
                logger.warning(f"Schemas path {self.schemas_path} does not exist.")

            # 2. Load data files
            # For now, we explicitly load known data files.
            project_types_file = self.controlled_path / "project_types.yaml"
            if project_types_file.exists():
                logger.info(f"Loading data: {project_types_file}")
                # load_data_files returns a list of validated models
                data = load_data_files(str(project_types_file))
                if data:
                    self._controlled_data["project_types"] = data

            logger.info("Controlled data loaded successfully.")

        except Exception as e:
            logger.error(f"Failed to load controlled data: {e}")
            raise

    def get_controlled_data(self, key: str) -> Any:
        """Retrieves loaded controlled data by key."""
        return self._controlled_data.get(key)

    def refresh_controlled_data(self) -> None:
        """Reloads controlled data from disk (useful after git operations)."""
        self.load_controlled_data()
