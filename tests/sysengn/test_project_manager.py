import pytest
import sqlite3
import os
import subprocess
from unittest.mock import MagicMock, patch
from datetime import datetime
from sysengn.core.project_manager import ProjectManager


@pytest.fixture
def test_db_path(tmp_path):
    # Setup a temp db for testing
    d = tmp_path / "test.db"
    return str(d)


@pytest.fixture
def project_manager(test_db_path, tmp_path):
    # Initialize DB
    from sysengn.db.database import init_db

    init_db(test_db_path)
    # Use tmp_path as root_dir for projects
    return ProjectManager(db_path=test_db_path, root_dir=tmp_path)


@patch("subprocess.run")
def test_create_project(mock_run, project_manager):
    project = project_manager.create_project(
        name="Test Project",
        description="A test project",
        owner_id="user1",
    )

    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert project.owner_id == "user1"
    # Path should be root_dir/owner_id/name
    expected_path = os.path.join(project_manager.root_dir, "user1", "Test Project")
    assert project.path == expected_path
    assert project.repo_url is None
    assert project.status == "Active"
    assert project.id is not None
    assert isinstance(project.created_at, datetime)
    assert isinstance(project.updated_at, datetime)

    # Verify git init was called
    mock_run.assert_called_with(
        ["git", "init"], cwd=expected_path, check=True, capture_output=True, text=True
    )
    # Verify directory was created
    assert os.path.exists(expected_path)
    assert os.path.isdir(expected_path)


@patch("subprocess.run")
def test_create_project_git_error(mock_run, project_manager):
    """Test handling of git init failure."""
    mock_run.side_effect = subprocess.CalledProcessError(
        1, ["git", "init"], stderr="Git error"
    )

    with pytest.raises(Exception) as excinfo:
        project_manager.create_project(
            name="Fail Project",
            description="A failed project",
            owner_id="user1",
        )

    assert "Git operation failed" in str(excinfo.value)

    # Verify no DB entry was created (rollback or never inserted)
    # Since the git op happens before DB insert in the code, this is implicit,
    # but good to verify the state.
    projects = project_manager.get_all_projects()
    assert len(projects) == 0


@patch("subprocess.run")
def test_create_project_with_repo(mock_run, project_manager):
    repo_url = "https://github.com/example/repo.git"
    project = project_manager.create_project(
        name="Cloned Project",
        description="A cloned project",
        owner_id="user1",
        repo_url=repo_url,
    )

    expected_path = os.path.join(project_manager.root_dir, "user1", "Cloned Project")
    assert project.path == expected_path
    assert project.repo_url == repo_url

    # Verify git clone was called
    mock_run.assert_called_with(
        ["git", "clone", repo_url, expected_path],
        check=True,
        capture_output=True,
        text=True,
    )


@patch("subprocess.run")
def test_get_all_projects(mock_run, project_manager):
    # Create a few projects
    p1 = project_manager.create_project("Project 1", "Desc 1", "user1")
    p2 = project_manager.create_project("Project 2", "Desc 2", "user1")

    projects = project_manager.get_all_projects()

    assert len(projects) == 2
    # Verify ordering (updated_at DESC)
    # Since p2 was created after p1, it should be first
    assert projects[0].id == p2.id
    assert projects[1].id == p1.id

    expected_path_p2 = os.path.join(project_manager.root_dir, "user1", "Project 2")
    assert projects[0].path == expected_path_p2


@patch("subprocess.run")
def test_create_project_db_error(mock_run, project_manager):
    # Mock connection to raise error
    with patch("sysengn.core.project_manager.get_connection") as mock_conn:
        mock_conn.side_effect = sqlite3.Error("DB Error")

        with pytest.raises(sqlite3.Error):
            project_manager.create_project("Fail", "Fail", "user1")


def test_get_all_projects_db_error(project_manager):
    with patch("sysengn.core.project_manager.get_connection") as mock_conn:
        mock_conn.side_effect = sqlite3.Error("DB Error")

        # Should catch error and return empty list
        projects = project_manager.get_all_projects()
        assert projects == []


@patch("sysengn.core.project_manager.get_connection")
def test_get_project_found(mock_get_conn):
    """Test retrieving a specific project."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock DB row
    now = datetime.now()
    mock_cursor.fetchone.return_value = {
        "id": "123",
        "name": "Test Project",
        "description": "Desc",
        "status": "Active",
        "owner_id": "u1",
        "path": "/tmp/test",
        "repo_url": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    pm = ProjectManager()
    project = pm.get_project("123")

    assert project is not None
    assert project.id == "123"
    assert project.name == "Test Project"
    assert project.path == "/tmp/test"
    assert isinstance(project.created_at, datetime)


@patch("sysengn.core.project_manager.get_connection")
def test_get_project_not_found(mock_get_conn):
    """Test retrieving a non-existent project."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None

    pm = ProjectManager()
    project = pm.get_project("999")

    assert project is None


@patch("sysengn.core.project_manager.get_connection")
def test_get_project_db_error(mock_get_conn):
    """Test database error handling during get_project."""
    mock_get_conn.side_effect = sqlite3.Error("DB Error")

    pm = ProjectManager()
    project = pm.get_project("123")

    assert project is None
