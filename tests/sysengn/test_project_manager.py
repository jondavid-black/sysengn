import pytest
import sqlite3
from unittest.mock import patch
from datetime import datetime
from sysengn.project_manager import ProjectManager


@pytest.fixture
def test_db_path(tmp_path):
    # Setup a temp db for testing
    d = tmp_path / "test.db"
    return str(d)


@pytest.fixture
def project_manager(test_db_path):
    # Initialize DB
    from sysengn.db.database import init_db

    init_db(test_db_path)
    return ProjectManager(db_path=test_db_path)


def test_create_project(project_manager):
    project = project_manager.create_project(
        name="Test Project", description="A test project", owner_id="user1"
    )

    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert project.owner_id == "user1"
    assert project.status == "Active"
    assert project.id is not None
    assert isinstance(project.created_at, datetime)
    assert isinstance(project.updated_at, datetime)


def test_get_all_projects(project_manager):
    # Create a few projects
    p1 = project_manager.create_project("Project 1", "Desc 1", "user1")
    p2 = project_manager.create_project("Project 2", "Desc 2", "user1")

    projects = project_manager.get_all_projects()

    assert len(projects) == 2
    # Verify ordering (updated_at DESC)
    # Since p2 was created after p1, it should be first
    assert projects[0].id == p2.id
    assert projects[1].id == p1.id


def test_create_project_db_error(project_manager):
    # Mock connection to raise error
    with patch("sysengn.project_manager.get_connection") as mock_conn:
        mock_conn.side_effect = sqlite3.Error("DB Error")

        with pytest.raises(sqlite3.Error):
            project_manager.create_project("Fail", "Fail", "user1")


def test_get_all_projects_db_error(project_manager):
    with patch("sysengn.project_manager.get_connection") as mock_conn:
        mock_conn.side_effect = sqlite3.Error("DB Error")

        # Should catch error and return empty list
        projects = project_manager.get_all_projects()
        assert projects == []
