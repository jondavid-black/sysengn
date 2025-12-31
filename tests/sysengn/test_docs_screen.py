import flet as ft
from unittest.mock import MagicMock
from sysengn.ui.docs.docs_screen import DocsScreen
from sysengn.core.auth import User


def test_docs_screen_structure():
    """Verify DocsScreen structure and content."""
    mock_page = MagicMock(spec=ft.Page)
    mock_user = MagicMock(spec=User)
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"

    docs_screen = DocsScreen(mock_page, mock_user)

    assert isinstance(docs_screen, ft.Container)
    assert isinstance(docs_screen.content, ft.Column)

    column = docs_screen.content
    controls = column.controls

    # Check Title
    title_row = controls[0]
    assert isinstance(title_row, ft.Row)
    title_text = title_row.controls[0]
    assert isinstance(title_text, ft.Text)
    assert str(title_text.value) == "Documentation"

    # Check Placeholder Content
    placeholder_container = controls[2]  # Index 2 is the main content container
    assert isinstance(placeholder_container, ft.Container)

    placeholder_col = placeholder_container.content
    assert isinstance(placeholder_col, ft.Column)

    # Check for icon
    icon = placeholder_col.controls[0]
    assert isinstance(icon, ft.Icon)
    assert icon.name == ft.Icons.LIBRARY_BOOKS

    # Check for module text
    module_text = placeholder_col.controls[1]
    assert isinstance(module_text, ft.Text)
    assert str(module_text.value) == "Documentation Module"
