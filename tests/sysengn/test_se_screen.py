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
        path="/tmp/test",
        repo_url=None,
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
    # Container -> Row -> [Rail, Drawer, Divider, Main Content(Container)]
    assert isinstance(screen, ft.Container)
    row = screen.content
    assert isinstance(row, ft.Row)
    assert len(row.controls) == 4

    # Check Rail
    rail = row.controls[0]
    assert isinstance(rail, ft.NavigationRail)
    assert rail.destinations is not None
    assert len(rail.destinations) == 3

    # Check Drawer
    drawer = row.controls[1]
    assert isinstance(drawer, ft.Container)

    # Check Main Content
    main_content_container = row.controls[3]
    assert isinstance(main_content_container, ft.Container)

    main_col = main_content_container.content  # type: ignore
    assert isinstance(main_col, ft.Column)

    header_row = main_col.controls[0]  # type: ignore
    assert isinstance(header_row, ft.Row)

    # Check Header Text
    header_text = header_row.controls[0]  # type: ignore
    assert isinstance(header_text, ft.Text)
    assert "MBSE: Test Project" == header_text.value

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

    # Verify Structure
    assert isinstance(screen, ft.Container)
    row = screen.content
    assert isinstance(row, ft.Row)

    main_content_container = row.controls[3]
    main_col = main_content_container.content  # type: ignore

    header_row = main_col.controls[0]  # type: ignore
    header_text = header_row.controls[0]  # type: ignore

    assert "MBSE: Unknown Project" == header_text.value


@patch("sysengn.ui.se.se_screen.ProjectManager")
def test_se_screen_rail_navigation(mock_pm_cls):
    """Verify SEScreen navigation rail changes content."""
    mock_pm = mock_pm_cls.return_value
    mock_project = Project(
        id="123",
        name="Test Project",
        description="Desc",
        owner_id="u1",
        status="Active",
        path="/tmp/test",
        repo_url=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_pm.get_project.return_value = mock_project

    mock_page = MagicMock(spec=ft.Page)
    mock_page.session.get.return_value = "123"
    mock_user = MagicMock(spec=User)

    screen = SEScreen(mock_page, mock_user)

    # Manually attach mock page to drawer container ref since it's not actually added to a page layout
    # This mocks the behavior of Flet's internal referencing when control is mounted
    mock_container = MagicMock(spec=ft.Container)
    # We need to simulate that the control is "on the page" so update() doesn't fail
    # or just mock the reference to return a mock object that absorbs update()
    screen.drawer_container_ref.current = mock_container

    # Simulate rail change event to index 1 (Containment Tree)
    mock_event = MagicMock()
    mock_event.control.selected_index = 1
    screen.on_rail_change(mock_event)

    # Verify drawer content updated via the mock container we injected
    assert mock_container.update.called
    assert mock_container.content is not None

    # Let's manually invoke _build_tree_view and check structure
    tree_view = screen._build_tree_view(
        "Containment", screen.containment_data, ft.Icons.ADD_BOX
    )
    assert isinstance(tree_view, ft.Column)
    assert isinstance(tree_view.controls[0], ft.Row)  # Header
    assert isinstance(tree_view.controls[2], ft.Container)  # Tree container

    # Check tree nodes generation
    nodes = screen._build_tree_nodes(screen.containment_data)
    assert len(nodes) > 0
    assert isinstance(nodes[0], ft.Container)

    # Simulate rail change to index 2 (Specification Tree)
    mock_event.control.selected_index = 2
    screen.on_rail_change(mock_event)
    assert mock_container.update.call_count == 2

    # Simulate rail change to index 0 (File System)
    mock_event.control.selected_index = 0
    screen.on_rail_change(mock_event)
    assert mock_container.update.call_count == 3

    # Verify drawer content updated
    assert isinstance(screen.drawer_content, ft.Text)  # Initial was Text
    # Since we can't easily check the *new* content object reference without mocking internal builds more,
    # we can check if update() was called on the ref
    # Ideally we'd inspect screen.drawer_container_ref.current.content, but that requires setting .current manually

    # Let's manually invoke _build_tree_view and check structure
    tree_view = screen._build_tree_view(
        "Containment", screen.containment_data, ft.Icons.ADD_BOX
    )
    assert isinstance(tree_view, ft.Column)
    assert isinstance(tree_view.controls[0], ft.Row)  # Header
    assert isinstance(tree_view.controls[2], ft.Container)  # Tree container

    # Check tree nodes generation
    nodes = screen._build_tree_nodes(screen.containment_data)
    assert len(nodes) > 0
    assert isinstance(nodes[0], ft.Container)

    # Simulate rail change to index 2 (Specification Tree)
    mock_event.control.selected_index = 2
    screen.on_rail_change(mock_event)

    # Simulate rail change to index 0 (File System)
    mock_event.control.selected_index = 0
    screen.on_rail_change(mock_event)
