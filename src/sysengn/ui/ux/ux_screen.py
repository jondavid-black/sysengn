import flet as ft
from sysengn.core.auth import User


def UXScreen(page: ft.Page, user: User) -> ft.Control:
    """The User Experience (UX) Screen component."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "UX Design Dashboard",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "This is a placeholder for the UX Design tools.",
                    size=16,
                    color=ft.Colors.GREY_500,
                ),
                ft.Divider(height=40),
                ft.Icon(
                    name=ft.Icons.DESIGN_SERVICES, size=100, color=ft.Colors.PURPLE
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=20,
        expand=True,
    )
