import pytest
from unittest.mock import MagicMock
import flet as ft
from sysengn.core.auth import Role, User
from sysengn.ui.admin_screen import admin_page


@pytest.fixture
def mock_page():
    return MagicMock(spec=ft.Page)


def test_admin_page_unauthorized(mock_page):
    # Setup non-admin user
    user = User(id="1", email="user@test.com", roles=[Role.USER])
    mock_page.session.get.return_value = user

    on_back = MagicMock()

    admin_page(mock_page, on_back)

    # Should show error snackbar
    assert mock_page.overlay.append.called
    assert isinstance(mock_page.overlay.append.call_args[0][0], ft.SnackBar)

    # Should NOT clean page or set title
    mock_page.clean.assert_not_called()


def test_admin_page_authorized(mock_page):
    # Setup admin user
    user = User(id="1", email="admin@test.com", roles=[Role.ADMIN])
    mock_page.session.get.return_value = user

    on_back = MagicMock()

    admin_page(mock_page, on_back)

    # Should build page
    mock_page.clean.assert_called_once()
    assert mock_page.title == "SysEngn - Admin"
    assert isinstance(mock_page.appbar, ft.AppBar)

    # Check content
    mock_page.add.assert_called_once()
    content = mock_page.add.call_args[0][0]
    assert isinstance(content, ft.Column)

    # Test back button
    back_btn = mock_page.appbar.leading
    assert isinstance(back_btn, ft.IconButton)

    # Simulate click
    if back_btn.on_click:
        back_btn.on_click(
            ft.ControlEvent(
                target="mock", name="click", data="", control=back_btn, page=mock_page
            )
        )
    on_back.assert_called_once()
