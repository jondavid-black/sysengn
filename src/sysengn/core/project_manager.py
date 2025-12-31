import sqlite3
import uuid
from datetime import datetime
from typing import Optional, List
import logging

from sysengn.db.database import get_connection
from sysengn.data.models import Project

logger = logging.getLogger(__name__)


class ProjectManager:
    """Manages project-related operations."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def create_project(self, name: str, description: str, owner_id: str) -> Project:
        """Creates a new project.

        Args:
            name: The name of the project.
            description: A description of the project.
            owner_id: The ID of the user creating the project.

        Returns:
            The created Project object.
        """
        project_id = str(uuid.uuid4())
        now = datetime.now()

        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO projects (id, name, description, status, owner_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                # Use isoformat() string to avoid deprecation warning for default adapter
                (
                    project_id,
                    name,
                    description,
                    "Active",
                    owner_id,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            conn.commit()

            return Project(
                id=project_id,
                name=name,
                description=description,
                status="Active",
                owner_id=owner_id,
                created_at=now,
                updated_at=now,
            )
        except sqlite3.Error as e:
            logger.error(f"Error creating project: {e}")
            raise
        finally:
            conn.close()

    def get_all_projects(self) -> List[Project]:
        """Retrieves all projects.

        Returns:
            A list of Project objects.
        """
        conn = None
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
            rows = cursor.fetchall()

            projects = []
            for row in rows:
                # Convert string timestamps back to datetime objects if needed
                # SQLite stores them as strings by default for TIMESTAMP types usually
                # But here we rely on the fact we inserted datetime objects.
                # The python sqlite3 adapter handles some of this, but we might get strings back.

                created_at = row["created_at"]
                updated_at = row["updated_at"]

                # Ensure type safety for datetime fields
                final_created_at: datetime
                final_updated_at: datetime

                if isinstance(created_at, str):
                    try:
                        final_created_at = datetime.fromisoformat(created_at)
                    except ValueError:
                        final_created_at = datetime.now()
                elif isinstance(created_at, datetime):
                    final_created_at = created_at
                else:
                    final_created_at = datetime.now()

                if isinstance(updated_at, str):
                    try:
                        final_updated_at = datetime.fromisoformat(updated_at)
                    except ValueError:
                        final_updated_at = datetime.now()
                elif isinstance(updated_at, datetime):
                    final_updated_at = updated_at
                else:
                    final_updated_at = datetime.now()

                projects.append(
                    Project(
                        id=row["id"],
                        name=row["name"],
                        description=row["description"],
                        status=row["status"],
                        owner_id=row["owner_id"],
                        created_at=final_created_at,
                        updated_at=final_updated_at,
                    )
                )
            return projects
        except sqlite3.Error as e:
            logger.error(f"Error fetching projects: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieves a specific project by ID.

        Args:
            project_id: The ID of the project to retrieve.

        Returns:
            The Project object if found, otherwise None.
        """
        conn = None
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()

            if not row:
                return None

            # Helper to parse datetime safely (similar to get_all_projects)
            def parse_dt(dt_val):
                if isinstance(dt_val, str):
                    try:
                        return datetime.fromisoformat(dt_val)
                    except ValueError:
                        return datetime.now()
                elif isinstance(dt_val, datetime):
                    return dt_val
                return datetime.now()

            return Project(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                status=row["status"],
                owner_id=row["owner_id"],
                created_at=parse_dt(row["created_at"]),
                updated_at=parse_dt(row["updated_at"]),
            )
        except sqlite3.Error as e:
            logger.error(f"Error fetching project {project_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
