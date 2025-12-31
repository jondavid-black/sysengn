import flet as ft
from typing import Callable
from sysengn.core.auth import (
    get_oauth_providers,
    authenticate_local_user,
)


def login_page(
    page: ft.Page, on_login_success: Callable[[], None], allow_passwords: bool = False
) -> None:
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
        pass

    content: list[ft.Control] = [
        ft.Image(src="sysengn_splash.png", width=300),
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
                on_login_success()
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
