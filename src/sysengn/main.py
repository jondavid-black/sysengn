import argparse
import os
import flet as ft

from sysengn.core.auth import (
    User,
    Role,
    update_user_theme_preference,
)
from sysengn.ui.login_screen import login_page
from sysengn.ui.admin_screen import admin_page


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

    def build_banner(
        page: ft.Page, user: User, on_tab_change
    ) -> tuple[ft.Container, ft.Tabs, ft.CircleAvatar]:
        # Left: Icon, Name, Project Dropdown, Workspace Dropdown

        # We need access to projects for the dropdown
        from sysengn.core.project_manager import ProjectManager

        pm = ProjectManager()
        projects = pm.get_all_projects()

        project_options = [ft.dropdown.Option(key=p.id, text=p.name) for p in projects]

        # Set default active project to first available, or empty if none
        initial_project_id = projects[0].id if projects else None

        # Only override session if not already set or invalid
        current_session_project = page.session.get("current_project_id")
        if not current_session_project and initial_project_id:
            page.session.set("current_project_id", initial_project_id)  # type: ignore
        elif current_session_project:
            # Validate it still exists
            if not any(p.id == current_session_project for p in projects):
                page.session.set("current_project_id", initial_project_id)  # type: ignore

        # Get final effective project ID
        active_project_id = page.session.get("current_project_id")

        def on_project_change(e):
            selected_id = e.control.value
            if selected_id:
                page.session.set("current_project_id", selected_id)  # type: ignore
                # Refresh current view if it depends on project
                # We can trigger tab change to reload current tab or just notify
                # For now, let's just update the banner dropdown
                project_dropdown.update()

                # If currently on SE screen, we might want to refresh content area
                # A simple way is to re-trigger change_tab with current index
                current_tab_idx = tabs.selected_index
                if current_tab_idx == 1:  # MBSE Tab
                    change_tab(1)

        project_dropdown = ft.Dropdown(
            width=200,
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=0),
            # Default to active project
            value=active_project_id,
            options=project_options,
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
            border_radius=5,
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Select Active Project",
            on_change=on_project_change,
        )

        workspace_dropdown = ft.Dropdown(
            width=200,
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=0),
            value="main",
            options=[
                ft.dropdown.Option("main"),
                ft.dropdown.Option("dev"),
                ft.dropdown.Option("test"),
                ft.dropdown.Option("+ Add New Workspace"),
            ],
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
            border_radius=5,
        )

        # Left: Icon, Name, Project Dropdown, Workspace Dropdown
        left_section = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Image(
                        src="sysengn_logo_core_tiny_transparent.png",
                        width=55,
                        height=45,
                        tooltip="Go to Home",
                    ),
                    on_click=lambda _: on_tab_change(0),
                ),
                ft.Container(width=10),
                project_dropdown,
                ft.Container(width=10),
                workspace_dropdown,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Center: Tabs
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            indicator_color=ft.Colors.BLUE_200,
            label_color=ft.Colors.BLUE_200,
            unselected_label_color=ft.Colors.GREY_400,
            divider_color="transparent",
            tabs=[
                ft.Tab(text="Home"),
                ft.Tab(text="MBSE"),
                ft.Tab(text="UX"),
                ft.Tab(text="Docs"),
            ],
            on_change=lambda e: on_tab_change(e.control.selected_index),
        )

        # Right: Search, Theme Toggle, Avatar
        search_box = ft.TextField(
            hint_text="Search...",
            height=40,
            text_size=14,
            content_padding=ft.padding.only(left=10, bottom=10),
            width=200,
            border_radius=20,
            prefix_icon=ft.Icons.SEARCH,
            bgcolor=ft.Colors.GREY_800,
            border_color=ft.Colors.TRANSPARENT,
            color=ft.Colors.WHITE,
            hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
        )

        def toggle_theme(e):
            new_mode = (
                ft.ThemeMode.LIGHT
                if page.theme_mode == ft.ThemeMode.DARK
                else ft.ThemeMode.DARK
            )
            page.theme_mode = new_mode
            e.control.icon = (
                ft.Icons.DARK_MODE
                if page.theme_mode == ft.ThemeMode.LIGHT
                else ft.Icons.LIGHT_MODE
            )
            page.update()

            # Update preference in DB and session
            user.theme_preference = (
                "LIGHT" if new_mode == ft.ThemeMode.LIGHT else "DARK"
            )
            update_user_theme_preference(user.id, user.theme_preference)

        theme_icon = ft.IconButton(
            ft.Icons.DARK_MODE
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE,
            on_click=toggle_theme,
            tooltip="Toggle Dark Mode",
            icon_color=ft.Colors.GREY_400,
        )

        user_initials = user.name[0].upper() if user.name else user.email[0].upper()

        # If user has first and last name, show those initials
        if user.first_name and user.last_name:
            user_initials = f"{user.first_name[0].upper()}{user.last_name[0].upper()}"

        avatar = ft.CircleAvatar(
            content=ft.Text(user_initials, color=ft.Colors.WHITE),
            bgcolor=user.preferred_color if user.preferred_color else ft.Colors.BLUE,
            tooltip=f"{user.name or user.email}",
        )

        # Avatar Menu (Logout, Admin)
        avatar_menu = ft.PopupMenuButton(
            content=avatar,
            items=[
                item
                for item in [
                    ft.PopupMenuItem(
                        text="Profile",
                        icon=ft.Icons.PERSON,
                        on_click=lambda e: change_tab(4),  # 4 will be profile
                    ),
                    ft.PopupMenuItem(
                        text="Admin Panel",
                        icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                        on_click=lambda e: admin_page(page, lambda: back_to_main(page)),
                    )
                    if user.has_role(Role.ADMIN)
                    else None,  # type: ignore
                    ft.PopupMenuItem(
                        text="Logout",
                        icon=ft.Icons.LOGOUT,
                        on_click=lambda e: logout(page),
                    ),
                ]
                if item is not None
            ],
        )

        right_section = ft.Row(
            controls=[
                search_box,
                ft.Container(width=10),
                theme_icon,
                ft.Container(width=10),
                avatar_menu,
            ],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        banner_row = ft.Row(
            controls=[left_section, tabs, right_section],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

        return (
            ft.Container(
                content=banner_row,
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                bgcolor="#36454F",  # Charcoal
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
            ),
            tabs,
            avatar,
        )

    # Setup Page Layout
    page.padding = 0
    page.appbar = None  # Remove default AppBar

    content_area = ft.Container(expand=True, padding=20)

    # Reference to tabs control to break circular dependency
    tabs_ref: list[ft.Tabs] = []

    # Reference to avatar control
    avatar_ref: list[ft.CircleAvatar] = []

    def update_avatar():
        if avatar_ref:
            av = avatar_ref[0]
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
        if index >= 0 and tabs_ref:
            tabs_control = tabs_ref[0]
            tabs_control.selected_index = index
            if tabs_control.page:
                tabs_control.update()
        else:
            # If going home (-1) or no tabs, try to reset tabs selection if we are "out" of tabs
            if tabs_ref:
                tabs_control = tabs_ref[0]
                # If index is out of range (like 4 for profile), we might want to unselect all if possible,
                # but Flet tabs always select one.
                # So maybe we just don't update the visual tab selection if it's a hidden screen like profile?
                # Actually, 4 is not in the tabs list [0,1,2,3].
                # If we set selected_index to something invalid, it might error or do nothing.
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

    banner, tabs_control, avatar_control = build_banner(page, user, change_tab)
    tabs_ref.append(tabs_control)
    avatar_ref.append(avatar_control)

    change_tab(0)  # Initialize with Home Screen

    page.clean()
    page.add(
        ft.Column(
            controls=[banner, content_area],
            expand=True,
            spacing=0,
        )
    )


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
