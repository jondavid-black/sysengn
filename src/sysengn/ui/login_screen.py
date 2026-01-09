import flet as ft
from typing import Callable
from sysengn.core.auth import get_oauth_providers
from sysengn.ui.components.login_view import LoginView


def login_page(
    page: ft.Page,
    on_login_success: Callable[[], None],
    allow_passwords: bool = False,
    app_name: str = "SysEngn",
    icon: str = "sysengn_splash.png",
) -> None:
    """The login page of the application."""
    page.title = f"{app_name} - Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    providers = get_oauth_providers()

    login_view = LoginView(
        page=page,
        on_login_success=on_login_success,
        icon=icon,
        app_name=app_name,
        allow_passwords=allow_passwords,
        oauth_providers=providers,
    )

    page.add(login_view)
