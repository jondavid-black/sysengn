import argparse
import os
import flet as ft

from sysengn.core.auth import (
    User,
    Role,
)
from sysengn.ui.login_screen import login_page
from sysengn.ui.admin_screen import admin_page
from sysengn.ui.components.app_bar import SysEngnAppBar
from sysengn.ui.components.resizeable_panel import ResizeableSidePanel
from sysengn.ui.components.terminal import TerminalComponent


def load_env_file(filepath: str = ".env") -> None:
    """Loads environment variables from a .env file using the standard library."""
    if not os.path.exists(filepath):
        return

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Split on the first =
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]

                # Set environment variable if not already set
                if key and key not in os.environ:
                    os.environ[key] = value


def get_greeting() -> str:
    """Returns the application greeting message.

    Returns:
        The greeting string.
    """
    return "Hello from SysEngn!"


def main_page(page: ft.Page) -> None:
    """The main page of the application.

    Args:
        page: The Flet page object to construct the UI on.
    """

    # Check session for manually logged in user (local auth fallback)
    user = page.session.get("user")  # type: ignore

    # If not in session, check flet auth
    if not user and page.auth and page.auth.user:  # type: ignore
        # Convert flet user to our User model
        # In a real app we would fetch roles from DB based on ID
        user = User(
            id=page.auth.user.id,  # type: ignore
            email=page.auth.user.email if page.auth.user.email else "unknown",  # type: ignore
            name=page.auth.user.name,  # type: ignore
            roles=[Role.USER],  # Default role
            theme_preference="DARK",  # Default for oauth user until we fetch from DB
        )
        page.session.set("user", user)  # type: ignore

    if not user:
        # Should not happen if flow is correct, but safe guard
        page.clean()
        page.add(ft.Text("Not authorized. Please login."))
        return

    page.title = "SysEngn"

    # Set theme based on user preference
    if user.theme_preference == "LIGHT":
        page.theme_mode = ft.ThemeMode.LIGHT
    else:
        page.theme_mode = ft.ThemeMode.DARK
    page.update()

    # -- New Banner & Layout Logic --

    # Mock Screens
    def get_mock_home_screen() -> ft.Control:
        from sysengn.ui.home_screen import HomeScreen

        return HomeScreen(page, user)

    def get_mock_se_screen() -> ft.Control:
        from sysengn.ui.se.se_screen import SEScreen

        return SEScreen(page, user)

    def get_mock_ux_screen() -> ft.Control:
        from sysengn.ui.ux.ux_screen import UXScreen

        return UXScreen(page, user)

    def get_mock_docs_screen() -> ft.Control:
        from sysengn.ui.docs.docs_screen import DocsScreen

        return DocsScreen(page, user)

    def get_user_profile_screen() -> ft.Control:
        from sysengn.ui.user_profile_screen import UserProfileScreen

        # When saving/cancelling, we might want to just go back to home or previous tab
        return UserProfileScreen(
            page, user, on_back=lambda: change_tab(0), on_save=update_avatar
        )

    # Setup Page Layout
    page.padding = 0
    page.appbar = None  # Remove default AppBar

    content_area = ft.Container(expand=True, padding=20)

    # Reference to app_bar control to break circular dependency
    app_bar_ref: list[SysEngnAppBar] = []

    def update_avatar():
        if app_bar_ref:
            app_bar = app_bar_ref[0]
            # Rebuild avatar
            # The simplest way is to update user props and let rebuild happen or manually update
            # Since SysEngnAppBar exposes avatar_control, we can update it
            av = app_bar.avatar_control
            user_initials = user.name[0].upper() if user.name else user.email[0].upper()
            if user.first_name and user.last_name:
                user_initials = (
                    f"{user.first_name[0].upper()}{user.last_name[0].upper()}"
                )

            if isinstance(av.content, ft.Text):
                av.content.value = user_initials
            av.bgcolor = (
                user.preferred_color if user.preferred_color else ft.Colors.BLUE
            )
            av.update()

    def change_tab(index: int):
        # Update tab selection only if it's one of the main tabs (0, 1, 2, 3)
        if index >= 0 and app_bar_ref:
            app_bar = app_bar_ref[0]
            tabs_control = app_bar.tabs_control
            tabs_control.selected_index = index
            if tabs_control.page:
                tabs_control.update()
        else:
            # If going home (-1) or no tabs, try to reset tabs selection if we are "out" of tabs
            if app_bar_ref:
                app_bar = app_bar_ref[0]
                # Pass for now
                pass

        if index == 0:
            content_area.content = get_mock_home_screen()
        elif index == 1:
            content_area.content = get_mock_se_screen()
        elif index == 2:
            content_area.content = get_mock_ux_screen()
        elif index == 3:
            content_area.content = get_mock_docs_screen()
        elif index == 4:
            content_area.content = get_user_profile_screen()

        if content_area.page:
            content_area.update()

    # Define tab names
    tabs_list = ["Home", "MBSE", "UX", "Docs"]

    # -- Custom Overlay / Layout Components --
    terminal_panel = ResizeableSidePanel(
        content=TerminalComponent(),
        visible=False,
    )
    # Position the panel on the right side of the Stack
    terminal_panel.right = 0
    terminal_panel.top = 0
    terminal_panel.bottom = 0

    def toggle_terminal():
        terminal_panel.toggle()
        page.update()

    app_bar = SysEngnAppBar(
        page=page,
        user=user,
        logo_path="sysengn_logo_core_tiny_transparent.png",
        on_tab_change=change_tab,
        tabs=tabs_list,
        on_logout=lambda: logout(page),
        on_profile=lambda: change_tab(4),
        on_admin=lambda: admin_page(page, lambda: back_to_main(page)),
        on_toggle_terminal=toggle_terminal,
    )
    app_bar_ref.append(app_bar)

    change_tab(0)  # Initialize with Home Screen

    page.clean()

    # Main Layout
    main_layout = ft.Column(
        controls=[app_bar, content_area],
        expand=True,
        spacing=0,
    )

    # We wrap the main layout in a container that expands
    main_container = ft.Container(
        content=main_layout,
        expand=True,
    )

    # The Overlay Layer
    # We add terminal_panel directly to the Stack.
    # By setting right=0, top=0, bottom=0, it docks to the right and stretches vertically.
    # Since it is a Row (ResizeableSidePanel), its width is determined by its content.
    # This prevents it from blocking clicks on the rest of the screen.

    stack = ft.Stack(
        controls=[
            main_container,
            terminal_panel,
        ],
        expand=True,
    )

    page.add(stack)


def back_to_main(page: ft.Page):
    """Returns to the main page."""
    page.clean()
    main_page(page)


def logout(page: ft.Page):
    page.logout()
    page.session.clear()  # type: ignore
    page.clean()
    allow_pass = page.session.get("allow_passwords")  # type: ignore
    login_page(
        page, on_login_success=lambda: main_page(page), allow_passwords=bool(allow_pass)
    )


def main() -> None:
    """Entry point for the application."""
    # Load environment variables from .env file
    load_env_file()

    parser = argparse.ArgumentParser(description="SysEngn Application")
    parser.add_argument("--web", action="store_true", help="Run in web browser")
    parser.add_argument(
        "--allow-passwords",
        action="store_true",
        help="Allow email/password login (Testing only)",
    )
    parser.add_argument(
        "--workdir",
        default=".",
        help="The working directory for projects (default: current directory)",
    )
    args = parser.parse_args()

    # Store workdir in environment for global access by ProjectManager
    os.environ["SYSENGN_WORKDIR"] = os.path.abspath(args.workdir)

    def app_main(page: ft.Page):
        # Initialize database
        from sysengn.db.database import init_db

        init_db()

        # Set default theme mode to DARK for login screen
        page.theme_mode = ft.ThemeMode.DARK

        # Enable window resizing and maximizing
        page.window.resizable = True  # Must be True for maximize to work
        page.window.maximizable = True  # Enables the maximize button
        page.window.minimizable = True  # Enables the minimize button

        page.session.set("allow_passwords", args.allow_passwords)  # type: ignore
        login_page(
            page,
            on_login_success=lambda: main_page(page),
            allow_passwords=args.allow_passwords,
            app_name="SysEngn",
            icon="sysengn_splash.png",
        )

    view = ft.AppView.WEB_BROWSER if args.web else ft.AppView.FLET_APP

    # Ensure assets directory is correctly resolved relative to this script
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")

    # We need to set a secret key for session/auth to work securely
    # ft.app(target=app_main, view=view, secret_key=os.getenv("APP_SECRET_KEY", "dev_secret_key"))
    # In 0.25.2 secret_key might not be in ft.app arguments directly?
    # It seems secret_key is not in ft.app arguments directly in 0.25.2.
    # Sessions might not be fully supported without it or it's handled differently.
    # However, let's try just running without it and see if session works (it might be insecure/in-memory).
    ft.app(
        target=app_main,
        view=view,
        assets_dir=assets_dir,
    )


if __name__ == "__main__":
    main()
