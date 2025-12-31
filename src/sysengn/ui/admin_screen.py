import flet as ft
from typing import Callable
from sysengn.core.auth import Role


def admin_page(page: ft.Page, on_back: Callable[[], None]) -> None:
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
        leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: on_back()),
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
