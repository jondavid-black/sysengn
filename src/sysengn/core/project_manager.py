import sqlite3
import uuid
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import logging

from sysengn.db.database import get_connection
from sysengn.data.models import Project

logger = logging.getLogger(__name__)


class ProjectManager:
    """Manages project-related operations."""

    def __init__(self, db_path: Optional[str] = None, root_dir: str | Path = "."):
        self.db_path = db_path
        self.root_dir = str(root_dir)

    def create_project(
        self,
        name: str,
        description: str,
        owner_id: str,
        repo_url: str | None = None,
    ) -> Project:
        """Creates a new project.

        Args:
            name: The name of the project.
            description: A description of the project.
            owner_id: The ID of the user creating the project.
            repo_url: Optional remote git repository URL.

        Returns:
            The created Project object.
        """
        project_id = str(uuid.uuid4())

        # Calculate path: root_dir/owner_id/name
        project_path = os.path.join(self.root_dir, owner_id, name)

        # Ensure directory exists
        try:
            os.makedirs(project_path, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating project directory {project_path}: {e}")
            raise

        # Git Integration
        try:
            if repo_url:
                # Clone repo
                # Check if directory is not empty (except .git if it exists? no, create just made it or it existed)
                if any(os.scandir(project_path)):
                    # If directory is not empty, git clone will fail unless the directory is empty.
                    # We'll let git clone fail naturally or we could check specifically.
                    # But common behavior is to expect empty dir for clone.
                    # However, os.makedirs(exist_ok=True) might imply we are reusing.
                    # If reusing, and it has stuff, we might want to skip clone or error out.
                    pass

                logger.info(f"Cloning {repo_url} into {project_path}")
                subprocess.run(
                    ["git", "clone", repo_url, project_path],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            else:
                # Init new repo
                logger.info(f"Initializing git repo in {project_path}")
                # Use cwd to run init inside the directory
                subprocess.run(
                    ["git", "init"],
                    cwd=project_path,
                    check=True,
                    capture_output=True,
                    text=True,
                )
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e.stderr}")
            # If git fails, we probably shouldn't create the DB entry?
            # Or should we clean up?
            # For now, let's propagate the failure so the caller knows.
            raise Exception(f"Git operation failed: {e.stderr}") from e

        now = datetime.now()

        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO projects (id, name, description, status, owner_id, path, repo_url, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                # Use isoformat() string to avoid deprecation warning for default adapter
                (
                    project_id,
                    name,
                    description,
                    "Active",
                    owner_id,
                    project_path,
                    repo_url,
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
                path=project_path,
                repo_url=repo_url,
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
                        path=row["path"],
                        repo_url=row["repo_url"],
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
                path=row["path"],
                repo_url=row["repo_url"],
                created_at=parse_dt(row["created_at"]),
                updated_at=parse_dt(row["updated_at"]),
            )
        except sqlite3.Error as e:
            logger.error(f"Error fetching project {project_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
