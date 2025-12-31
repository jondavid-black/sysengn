import flet as ft
from unittest.mock import MagicMock
from sysengn.ui.home_screen import HomeScreen
from sysengn.core.auth import User


def test_home_screen_structure():
    """Verify HomeScreen structure and content."""
    mock_page = MagicMock(spec=ft.Page)
    mock_user = MagicMock(spec=User)
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"

    home_screen = HomeScreen(mock_page, mock_user)

    assert isinstance(home_screen, ft.Container)
    assert isinstance(home_screen.content, ft.Column)

    column = home_screen.content
    controls = column.controls

    # Check Welcome Message
    welcome_text = controls[0]
    assert isinstance(welcome_text, ft.Text)
    # Cast value to str to satisfy pyright if it thinks it could be None
    assert "Welcome back, Test User!" in str(welcome_text.value)

    # Check Summary Cards
    cards_row = controls[3]  # Index 3 is the Row containing cards
    assert isinstance(cards_row, ft.Row)
    assert len(cards_row.controls) == 4  # 4 summary cards

    first_card_container = cards_row.controls[0]
    assert isinstance(first_card_container, ft.Container)

    # Check fallback for missing name
    mock_user.name = None
    home_screen_no_name = HomeScreen(mock_page, mock_user)
    assert isinstance(home_screen_no_name, ft.Container)
    # Type guard for content
    assert isinstance(home_screen_no_name.content, ft.Column)
    welcome_text_no_name = home_screen_no_name.content.controls[0]
    # Type guard for control
    assert isinstance(welcome_text_no_name, ft.Text)
    assert "Welcome back, test@example.com!" in str(welcome_text_no_name.value)
