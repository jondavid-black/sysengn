import flet as ft
from unittest.mock import MagicMock, patch
from sysengn.ui.pm.pm_screen import PMScreen
from sysengn.core.auth import User
from sysengn.data.models import Project
from datetime import datetime


@patch("sysengn.ui.pm.pm_screen.ProjectManager")
def test_pm_screen_empty(mock_pm_cls):
    """Verify PMScreen empty state."""
    mock_pm = mock_pm_cls.return_value
    mock_pm.get_all_projects.return_value = []

    mock_page = MagicMock(spec=ft.Page)
    mock_user = MagicMock(spec=User)

    screen = PMScreen(mock_page, mock_user)

    # Verify structure
    assert isinstance(screen, ft.Container)
    main_column = screen.content  # type: ignore
    assert isinstance(main_column, ft.Column)

    # Find the projects column (second item in main column, after header row and divider)
    projects_column = main_column.controls[2]
    assert isinstance(projects_column, ft.Column)

    # Check empty state content
    assert len(projects_column.controls) == 1
    empty_container = projects_column.controls[0]
    assert isinstance(empty_container, ft.Container)

    # Dig into empty message text
    empty_col = empty_container.content  # type: ignore
    # Type guard
    assert isinstance(empty_col, ft.Column)

    assert "No projects yet" in [
        c.value for c in empty_col.controls if isinstance(c, ft.Text)
    ]


@patch("sysengn.ui.pm.pm_screen.ProjectManager")
def test_pm_screen_with_projects(mock_pm_cls):
    """Verify PMScreen with projects."""
    mock_pm = mock_pm_cls.return_value

    # Setup mock projects
    p1 = Project(
        id="1",
        name="Project A",
        description="Desc A",
        owner_id="u1",
        status="Active",
        path="/tmp/p1",
        repo_url=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    p2 = Project(
        id="2",
        name="Project B",
        description="Desc B",
        owner_id="u1",
        status="Draft",
        path="/tmp/p2",
        repo_url=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    mock_pm.get_all_projects.return_value = [p1, p2]

    mock_page = MagicMock(spec=ft.Page)
    mock_user = MagicMock(spec=User)

    screen = PMScreen(mock_page, mock_user)

    main_column = screen.content  # type: ignore
    # Type guard
    assert isinstance(main_column, ft.Column)

    # We need to cast or ignore type check for dynamic attributes in tests
    projects_column = main_column.controls[2]  # type: ignore
    # Type guard
    assert isinstance(projects_column, ft.Column)

    # Should have 2 cards
    assert len(projects_column.controls) == 2  # type: ignore
    assert isinstance(projects_column.controls[0], ft.Card)  # type: ignore

    # Verify content of first card
    # Card.content -> Container.content -> Column.content -> [Row(Name), ...]
    card_container = projects_column.controls[0].content  # type: ignore
    assert isinstance(card_container, ft.Container)
    card_column = card_container.content  # type: ignore
    assert isinstance(card_column, ft.Column)

    # Project Name is in the first Row
    header_row = card_column.controls[0]  # type: ignore
    assert isinstance(header_row, ft.Row)
    name_text = header_row.controls[0]  # type: ignore
    assert isinstance(name_text, ft.Text)
    assert name_text.value == "Project A"


@patch("sysengn.ui.pm.pm_screen.ProjectManager")
def test_create_project_flow(mock_pm_cls):
    """Verify create project dialog flow."""
    mock_pm = mock_pm_cls.return_value
    mock_pm.get_all_projects.return_value = []

    mock_page = MagicMock(spec=ft.Page)
    mock_page.overlay = []  # Simulate overlay list
    mock_user = MagicMock(spec=User)
    mock_user.id = "user1"

    screen = PMScreen(mock_page, mock_user)

    # 1. Find "New Project" button
    main_column = screen.content  # type: ignore
    # Type guard
    assert isinstance(main_column, ft.Column)

    header_row = main_column.controls[0]  # type: ignore
    assert isinstance(header_row, ft.Row)
    new_btn = header_row.controls[1]  # type: ignore
    assert isinstance(new_btn, ft.ElevatedButton)
    assert isinstance(new_btn.content, ft.Row)
    # Pyright doesn't know controls is a list[Control] specifically for Row.controls sometimes or mock issues
    # but let's assume standard flet structure
    btn_text = new_btn.content.controls[1]  # type: ignore
    assert isinstance(btn_text, ft.Text)
    assert btn_text.value == "New Project"

    # 2. Click it -> Open Dialog
    # We need to access the closure functions.
    # Since we can't easily access closure functions from outside without returning them,
    # we simulate the UI interaction by triggering the event handler if we can reach it,
    # OR we verify the side effects on the dialog object which IS defined in the scope
    # but also hard to reach if not attached to the return object.

    # However, flet controls store event handlers.
    new_btn.on_click(None)  # type: ignore

    # Check if dialog was assigned to page
    assert hasattr(mock_page, "dialog")
    dialog = mock_page.dialog
    assert dialog.open is True
    assert dialog.title.value == "New Project"  # type: ignore

    # 3. Fill form and Create
    content_col = dialog.content  # type: ignore
    assert isinstance(content_col, ft.Column)
    name_field = content_col.controls[0]  # type: ignore
    desc_field = content_col.controls[1]  # type: ignore
    # path_field = content_col.controls[2] # Removed path field
    # repo_field = content_col.controls[2] # moved up

    name_field.value = "New App"  # type: ignore
    desc_field.value = "My Description"  # type: ignore
    # path_field.value = "/tmp/new_app" # auto-generated
    # repo_field.value = "" # default empty

    # IMPORTANT: Flet controls check if they are added to a page before update() is called.
    # In this test environment with mocks, we need to ensure the controls think they are attached.
    # We can mock the `page` property or `_Control__page` private attribute.
    # name_field._Control__page = mock_page
    # desc_field._Control__page = mock_page
    # repo_field._Control__page = mock_page

    # Find Create button in actions
    create_btn = dialog.actions[1]  # type: ignore
    assert isinstance(create_btn, ft.ElevatedButton)
    assert isinstance(create_btn.content, ft.Text)
    assert create_btn.content.value == "Create"  # type: ignore

    # Trigger Create
    create_btn.on_click(None)  # type: ignore

    # 4. Verify PM call and success
    mock_pm.create_project.assert_called_with(
        name="New App",
        description="My Description",
        owner_id="user1",
        # path="/tmp/new_app", # removed
        repo_url=None,
    )

    assert dialog.open is False
    assert mock_page.update.called

    # Check SnackBar
    assert len(mock_page.overlay) > 0
    assert isinstance(mock_page.overlay[0], ft.SnackBar)
