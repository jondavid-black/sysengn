import flet as ft
from sysengn.core.auth import User


def TeamScreen(page: ft.Page, user: User) -> ft.Control:
    """The Team Management Screen component."""
    return ft.Container(
        content=ft.Text("Mock Team Screen", size=30, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment(0, 0),
        expand=True,
    )
