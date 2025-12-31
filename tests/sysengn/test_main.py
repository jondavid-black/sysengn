import os
from unittest.mock import MagicMock, patch, mock_open

import flet as ft
from flet.auth.providers import GoogleOAuthProvider, GitHubOAuthProvider

from sysengn.main import (
    load_env_file,
    login_page,
    logout,
    main,
    main_page,
    get_greeting,
)


def test_get_greeting():
    """Verify the greeting message is correct."""
    assert get_greeting() == "Hello from SysEngn!"


# --- load_env_file Tests ---


def test_load_env_file_missing():
    """Verify load_env_file handles missing file gracefully."""
    with patch("os.path.exists", return_value=False):
        load_env_file("missing.env")
        # Should not raise exception


def test_load_env_file_loading():
    """Verify load_env_file parses file correctly."""
    env_content = """
    # Comment
    KEY1=value1
    KEY2 = value2
    KEY3="value3"
    KEY4='value4'
    EXISTING=newvalue
    """
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=env_content)),
        patch.dict(os.environ, {"EXISTING": "oldvalue"}, clear=True),
    ):
        load_env_file()

        assert os.environ["KEY1"] == "value1"
        assert os.environ["KEY2"] == "value2"
        assert os.environ["KEY3"] == "value3"
        assert os.environ["KEY4"] == "value4"
        assert os.environ["EXISTING"] == "oldvalue"  # Should not overwrite


# --- main_page Tests ---


def test_main_page_authenticated_session():
    """Verify the main page construction when user is authenticated via session."""
    mock_page = MagicMock(spec=ft.Page)
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    mock_page.session.get.return_value = mock_user

    main_page(mock_page)

    assert mock_page.title == "SysEngn"
    texts = [
        args[0].value
        for args, _ in mock_page.add.call_args_list
        if isinstance(args[0], ft.Text)
    ]
    assert "Logged in as: test@example.com" in texts


def test_main_page_authenticated_flet_auth():
    """Verify main page handles flet auth object."""
    mock_page = MagicMock(spec=ft.Page)
    mock_page.session.get.return_value = None

    # Setup mock flet auth user
    mock_auth_user = MagicMock()
    mock_auth_user.id = "auth_id"
    mock_auth_user.email = "auth@test.com"
    mock_auth_user.name = "Auth User"

    mock_page.auth.user = mock_auth_user

    main_page(mock_page)

    # Verify user was set in session
    assert mock_page.session.set.called
    assert mock_page.session.set.call_args[0][0] == "user"
    user_arg = mock_page.session.set.call_args[0][1]
    assert user_arg.email == "auth@test.com"

    texts = [
        args[0].value
        for args, _ in mock_page.add.call_args_list
        if isinstance(args[0], ft.Text)
    ]
    assert "Logged in as: auth@test.com" in texts


def test_main_page_unauthenticated():
    """Verify redirect when unauthenticated."""
    mock_page = MagicMock(spec=ft.Page)
    mock_page.session.get.return_value = None
    mock_page.auth.user = None

    main_page(mock_page)

    assert mock_page.clean.called
    texts = [
        args[0].value
        for args, _ in mock_page.add.call_args_list
        if isinstance(args[0], ft.Text)
    ]
    assert "Not authorized. Please login." in texts


# --- logout Tests ---


def test_logout():
    """Verify logout clears session and redirects."""
    mock_page = MagicMock(spec=ft.Page)
    mock_page.session.get.return_value = True  # allow_passwords=True

    logout(mock_page)

    assert mock_page.logout.called
    assert mock_page.session.clear.called
    assert mock_page.clean.called

    # Should rebuild login page
    assert mock_page.add.called
    # Check if login page title is set
    assert mock_page.title == "SysEngn - Login"


# --- login_page Tests ---


@patch("sysengn.main.get_oauth_providers")
def test_login_page_oauth_buttons(mock_get_providers):
    """Verify OAuth buttons are created."""
    mock_page = MagicMock(spec=ft.Page)

    # Mock providers
    google = MagicMock(spec=GoogleOAuthProvider)
    google.authorization_endpoint = "google.com"

    github = MagicMock(spec=GitHubOAuthProvider)
    github.authorization_endpoint = "github.com"

    mock_get_providers.return_value = [google, github]

    login_page(mock_page)

    # Dig into the column content to find buttons
    column = mock_page.add.call_args[0][0]
    assert isinstance(column, ft.Column)
    controls = column.controls

    buttons = [c for c in controls if isinstance(c, ft.ElevatedButton)]
    # Now that we always add the "Sign In" button, we expect 3 buttons if providers are present
    assert len(buttons) == 3

    # Filter for OAuth buttons
    oauth_buttons = [b for b in buttons if "Login with" in b.text]  # type: ignore
    assert len(oauth_buttons) == 2
    assert "Login with Google" in oauth_buttons[0].text  # type: ignore
    assert "Login with GitHub" in oauth_buttons[1].text  # type: ignore
    assert oauth_buttons[0].disabled
    assert oauth_buttons[1].disabled


def test_login_page_no_providers_message():
    """Verify message when no providers and no passwords allowed."""
    mock_page = MagicMock(spec=ft.Page)
    with patch("sysengn.main.get_oauth_providers", return_value=[]):
        # Even if allow_passwords is False, we force it to True internally now,
        # so we expect the login form, NOT the "No OAuth providers" message.
        login_page(mock_page, allow_passwords=False)

        column = mock_page.add.call_args[0][0]
        texts = [c.value for c in column.controls if isinstance(c, ft.Text)]

        # We expect "Or sign in with email" now instead of the error message
        assert "Or sign in with email" in texts
        assert "No OAuth providers configured." not in texts


def test_login_page_allow_passwords():
    """Verify password fields appear when allowed."""
    mock_page = MagicMock(spec=ft.Page)
    with patch("sysengn.main.get_oauth_providers", return_value=[]):
        login_page(mock_page, allow_passwords=True)

        column = mock_page.add.call_args[0][0]
        # Check for inputs
        inputs = [c for c in column.controls if isinstance(c, ft.TextField)]
        assert len(inputs) == 2  # Email and Password

        # Find Sign In button
        buttons = [c for c in column.controls if isinstance(c, ft.ElevatedButton)]
        signin_btn = next(b for b in buttons if b.text == "Sign In")  # type: ignore

        # Test Local Auth Logic - Success
        inputs[0].value = "user@test.com"
        inputs[1].value = "pass"

        with patch("sysengn.main.authenticate_local_user") as mock_auth:
            mock_user = MagicMock()
            mock_auth.return_value = mock_user

            mock_e = MagicMock(spec=ft.ControlEvent)
            if signin_btn.on_click:
                signin_btn.on_click(mock_e)

            assert mock_page.session.set.called
            assert mock_page.session.set.call_args[0][0] == "user"
            assert mock_page.clean.called

        # Test Local Auth Logic - Failure
        mock_page.reset_mock()
        with patch("sysengn.main.authenticate_local_user", return_value=None):
            if signin_btn.on_click:
                signin_btn.on_click(mock_e)

            assert mock_page.overlay.append.called
            assert isinstance(mock_page.overlay.append.call_args[0][0], ft.SnackBar)
            assert mock_page.update.called


# --- main entry point Tests ---


@patch("sysengn.main.ft.app")
@patch("sys.argv", ["sysengn"])
@patch("sysengn.main.load_env_file")
@patch("sysengn.db.database.init_db")  # Mock init_db to avoid DB errors
def test_main_default(mock_init_db, mock_load_env, mock_app):
    """Verify main entry point initialization."""
    main()

    assert mock_load_env.called
    assert mock_app.called
    _, kwargs = mock_app.call_args
    assert kwargs["view"] == ft.AppView.FLET_APP

    # Test the internal app_main function
    target_func = kwargs["target"]
    mock_page = MagicMock(spec=ft.Page)

    target_func(mock_page)

    assert mock_init_db.called  # Ensure init_db is called
    assert mock_page.session.set.called
    assert mock_page.add.called  # login_page called
    assert mock_page.title == "SysEngn - Login"
