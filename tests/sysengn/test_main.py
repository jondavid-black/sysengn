from unittest.mock import MagicMock, patch

import flet as ft

from sysengn.main import get_greeting, main, main_page


def test_get_greeting():
    """Verify the greeting message is correct."""
    assert get_greeting() == "Hello from SysEngn!"


def test_main_page():
    """Verify the main page construction."""
    mock_page = MagicMock(spec=ft.Page)
    main_page(mock_page)

    assert mock_page.title == "SysEngn"
    # Verify a Text control was added
    assert mock_page.add.called
    args, _ = mock_page.add.call_args
    assert isinstance(args[0], ft.Text)
    assert args[0].value == "Hello from SysEngn!"


@patch("sysengn.main.ft.app")
@patch("sys.argv", ["sysengn"])
def test_main_default(mock_app):
    """Verify the main entry point starts the flet app as desktop by default."""
    main()
    mock_app.assert_called_once_with(target=main_page, view=ft.AppView.FLET_APP)


@patch("sysengn.main.ft.app")
@patch("sys.argv", ["sysengn", "--web"])
def test_main_web(mock_app):
    """Verify the main entry point starts the flet app as web when requested."""
    main()
    mock_app.assert_called_once_with(target=main_page, view=ft.AppView.WEB_BROWSER)
