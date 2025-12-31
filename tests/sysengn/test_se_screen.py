import flet as ft
from unittest.mock import MagicMock, patch
from datetime import datetime
from sysengn.ui.se.se_screen import SEScreen
from sysengn.core.auth import User
from sysengn.data.models import Project


@patch("sysengn.ui.se.se_screen.ProjectManager")
def test_se_screen_no_project(mock_pm_cls):
    """Verify SEScreen state when no project is selected."""
    mock_page = MagicMock(spec=ft.Page)
    # Simulate empty session or "Select Project"
    mock_page.session.get.return_value = None

    mock_user = MagicMock(spec=User)

    screen = SEScreen(mock_page, mock_user)

    assert isinstance(screen, ft.Container)
    # Check for specific "No Project" indication
    # Structure: Container -> Column -> [Icon, Text("No Project Selected"), ...]
    content_col = screen.content  # type: ignore
    assert isinstance(content_col, ft.Column)

    # Check text content
    texts = [c.value for c in content_col.controls if isinstance(c, ft.Text)]
    assert "No Project Selected" in texts


@patch("sysengn.ui.se.se_screen.ProjectManager")
def test_se_screen_with_project(mock_pm_cls):
    """Verify SEScreen when a project is selected."""
    mock_pm = mock_pm_cls.return_value

    mock_project = Project(
        id="123",
        name="Test Project",
        description="Desc",
        owner_id="u1",
        status="Active",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_pm.get_project.return_value = mock_project

    mock_page = MagicMock(spec=ft.Page)
    mock_page.session.get.return_value = "123"

    mock_user = MagicMock(spec=User)

    screen = SEScreen(mock_page, mock_user)

    # Verify Project Manager called
    mock_pm.get_project.assert_called_with("123")

    # Verify Structure
    # Container -> Column -> [Row(Header), Divider, Container(Tabs)]
    main_col = screen.content  # type: ignore
    assert isinstance(main_col, ft.Column)

    header_row = main_col.controls[0]  # type: ignore
    assert isinstance(header_row, ft.Row)

    # Check Header Text
    header_text = header_row.controls[0]  # type: ignore
    assert isinstance(header_text, ft.Text)
    assert "SE: Test Project" == header_text.value

    # Check Tabs exist
    tabs_container = main_col.controls[2]  # type: ignore
    assert isinstance(tabs_container, ft.Container)
    tabs = tabs_container.content  # type: ignore
    assert isinstance(tabs, ft.Tabs)

    assert len(tabs.tabs) == 3
    assert tabs.tabs[0].text == "Requirements"
    assert tabs.tabs[1].text == "Functions"
    assert tabs.tabs[2].text == "Components"


@patch("sysengn.ui.se.se_screen.ProjectManager")
def test_se_screen_project_not_found(mock_pm_cls):
    """Verify SEScreen when session ID exists but project DB returns None."""
    mock_pm = mock_pm_cls.return_value
    mock_pm.get_project.return_value = None  # Project deleted?

    mock_page = MagicMock(spec=ft.Page)
    mock_page.session.get.return_value = "999"

    mock_user = MagicMock(spec=User)

    screen = SEScreen(mock_page, mock_user)

    main_col = screen.content  # type: ignore
    header_row = main_col.controls[0]  # type: ignore
    header_text = header_row.controls[0]  # type: ignore

    assert "SE: Unknown Project" == header_text.value
