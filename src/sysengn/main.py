import argparse
import os
import flet as ft

from sysengn.auth import (
    User,
    get_oauth_providers,
    authenticate_local_user,
    Role,
    update_user_theme_preference,
)


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


def login_page(page: ft.Page, allow_passwords: bool = False) -> None:
    """The login page of the application."""
    page.title = "SysEngn - Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def handle_login_button(provider):
        page.login(provider)  # type: ignore

    providers = get_oauth_providers()
    login_buttons = []

    for provider in providers:
        # Check provider type or endpoint to determine name
        name = "OAuth Provider"
        # In older flet versions or specific providers we might not have easy access to endpoint properties directly if not exposed.
        # But we know what we added.
        if "google" in getattr(provider, "authorization_endpoint", ""):
            name = "Google"
        elif "github" in getattr(provider, "authorization_endpoint", ""):
            name = "GitHub"

        # Fallback using class name if endpoints are not reliable/available
        if name == "OAuth Provider":
            if "Google" in provider.__class__.__name__:
                name = "Google"
            elif "GitHub" in provider.__class__.__name__:
                name = "GitHub"

        login_buttons.append(
            ft.ElevatedButton(
                content=ft.Text(f"Login with {name}"),
                on_click=lambda _, p=provider: handle_login_button(p),
                disabled=True,  # Disabled for now
            )
        )

    if not login_buttons and not allow_passwords:
        # Should not show this message if we have buttons even if disabled, but logic stands.
        # However, request says "disable but don't remove".
        pass

    content: list[ft.Control] = [
        ft.Text("Welcome to SysEngn", size=30, weight=ft.FontWeight.BOLD),
        ft.Text("Please sign in to continue", size=16),
        ft.Divider(),
        *login_buttons,
    ]

    # Always allow passwords for now as default
    if True:
        email_field = ft.TextField(label="Email", width=300)
        password_field = ft.TextField(label="Password", password=True, width=300)

        def handle_local_login(e):
            if not email_field.value or not password_field.value:
                page.overlay.append(
                    ft.SnackBar(ft.Text("Please enter email and password"), open=True)
                )
                page.update()
                return

            user = authenticate_local_user(email_field.value, password_field.value)
            if user:
                page.session.set("user", user)  # type: ignore
                page.clean()
                main_page(page)
            else:
                page.overlay.append(
                    ft.SnackBar(ft.Text("Invalid credentials"), open=True)
                )
                page.update()

        # Add on_submit event handler to both fields
        email_field.on_submit = handle_local_login
        password_field.on_submit = handle_local_login

        content.extend(
            [
                ft.Divider(),
                ft.Text("Or sign in with email", size=14),
                email_field,
                password_field,
                ft.ElevatedButton(
                    content=ft.Text("Sign In"), on_click=handle_local_login
                ),
            ]
        )

    page.add(
        ft.Column(
            controls=content,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


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
    def get_mock_pm_screen() -> ft.Control:
        from sysengn.pm_screen import PMScreen

        return PMScreen(page, user)

    def get_mock_se_screen() -> ft.Control:
        return ft.Container(
            content=ft.Text("Mock SE Screen", size=30, weight=ft.FontWeight.BOLD),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )

    def get_mock_team_screen() -> ft.Control:
        return ft.Container(
            content=ft.Text("Mock Team Screen", size=30, weight=ft.FontWeight.BOLD),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )

    def build_banner(page: ft.Page, user: User, on_tab_change) -> ft.Control:
        # Left: Icon, Name, Workspace Dropdown
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

        left_section = ft.Row(
            controls=[
                ft.Icon(ft.Icons.TERMINAL, size=24, color=ft.Colors.BLUE_200),
                ft.Text(
                    "SysEngn", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
                ),
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
                ft.Tab(text="PM"),
                ft.Tab(text="SE"),
                ft.Tab(text="Team"),
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
        avatar = ft.CircleAvatar(
            content=ft.Text(user_initials, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLUE,
            tooltip=f"{user.name or user.email}",
        )

        # Avatar Menu (Logout, Admin)
        avatar_menu = ft.PopupMenuButton(
            content=avatar,
            items=[
                item
                for item in [
                    ft.PopupMenuItem(
                        text="Admin Panel",
                        icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                        on_click=lambda e: admin_page(page),
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

        return ft.Container(
            content=banner_row,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor="#36454F",  # Charcoal
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 2),
            ),
        )

    # Setup Page Layout
    page.padding = 0
    page.appbar = None  # Remove default AppBar

    content_area = ft.Container(expand=True, padding=20)

    def change_tab(index: int):
        if index == 0:
            content_area.content = get_mock_pm_screen()
        elif index == 1:
            content_area.content = get_mock_se_screen()
        elif index == 2:
            content_area.content = get_mock_team_screen()
        if content_area.page:
            content_area.update()

    banner = build_banner(page, user, change_tab)
    change_tab(0)  # Initialize

    page.clean()
    page.add(
        ft.Column(
            controls=[banner, content_area],
            expand=True,
            spacing=0,
        )
    )


def admin_page(page: ft.Page) -> None:
    """The admin dashboard page."""
    # Double check permission in case of direct navigation (if we had routing)
    user = page.session.get("user")  # type: ignore
    if not user or not user.has_role(Role.ADMIN):
        page.overlay.append(ft.SnackBar(ft.Text("Unauthorized access!"), open=True))
        page.update()
        return

    page.clean()
    page.title = "SysEngn - Admin"

    page.appbar = ft.AppBar(
        title=ft.Text("Admin Dashboard"),
        leading=ft.IconButton(
            ft.Icons.ARROW_BACK, on_click=lambda e: back_to_main(page)
        ),
    )

    page.add(
        ft.Column(
            [
                ft.Text("Admin Dashboard", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("Welcome, Administrator.", size=16),
                ft.Container(
                    content=ft.Text(
                        "Sensitive System Settings (Mock)", color=ft.Colors.WHITE
                    ),
                    bgcolor=ft.Colors.RED_900,
                    padding=20,
                    border_radius=10,
                ),
            ]
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
    login_page(page, allow_passwords=bool(allow_pass))


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
    args = parser.parse_args()

    def app_main(page: ft.Page):
        # Initialize database
        from sysengn.db.database import init_db

        init_db()

        # Set default theme mode to DARK for login screen
        page.theme_mode = ft.ThemeMode.DARK

        page.session.set("allow_passwords", args.allow_passwords)  # type: ignore
        login_page(page, allow_passwords=args.allow_passwords)

    view = ft.AppView.WEB_BROWSER if args.web else ft.AppView.FLET_APP
    # We need to set a secret key for session/auth to work securely
    # ft.app(target=app_main, view=view, secret_key=os.getenv("APP_SECRET_KEY", "dev_secret_key"))
    # In 0.25.2 secret_key might not be in ft.app arguments directly?
    # It seems secret_key is not in ft.app signature in 0.25.2.
    # Sessions might not be fully supported without it or it's handled differently.
    # However, let's try just running without it and see if session works (it might be insecure/in-memory).
    ft.app(
        target=app_main,
        view=view,
    )


if __name__ == "__main__":
    main()
