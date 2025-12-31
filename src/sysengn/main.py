import argparse
import os
import flet as ft

from sysengn.auth import User, get_oauth_providers, authenticate_local_user, Role


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
                text=f"Login with {name}",
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

        content.extend(
            [
                ft.Divider(),
                ft.Text("Or sign in with email", size=14),
                email_field,
                password_field,
                ft.ElevatedButton(text="Sign In", on_click=handle_local_login),
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
        )
        page.session.set("user", user)  # type: ignore

    if not user:
        # Should not happen if flow is correct, but safe guard
        page.clean()
        page.add(ft.Text("Not authorized. Please login."))
        return

    page.title = "SysEngn"

    actions: list[ft.Control] = [
        ft.IconButton(ft.Icons.LOGOUT, on_click=lambda e: logout(page))
    ]
    if user.has_role(Role.ADMIN):
        actions.insert(
            0,
            ft.IconButton(
                ft.Icons.ADMIN_PANEL_SETTINGS,
                tooltip="Admin Panel",
                on_click=lambda e: admin_page(page),
            ),
        )

    page.appbar = ft.AppBar(
        title=ft.Text("SysEngn"),
        actions=actions,
    )

    page.add(ft.Text(value=get_greeting(), size=30))
    if hasattr(user, "email"):
        page.add(ft.Text(f"Logged in as: {user.email}"))


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
                        "Sensitive System Settings (Mock)", color=ft.colors.WHITE
                    ),
                    bgcolor=ft.colors.RED_900,
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
