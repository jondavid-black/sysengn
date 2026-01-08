import flet as ft
from sysengn.core.auth import User


def HomeScreen(page: ft.Page, user: User) -> ft.Container:
    """A mock Home / Dashboard screen."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    f"Welcome back, {user.name or user.email}!",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "This is your SysEngn Dashboard.", size=16, color=ft.Colors.GREY_500
                ),
                ft.Divider(height=40),
                ft.Row(
                    controls=[
                        _build_summary_card(
                            "Active Projects",
                            "3",
                            ft.Icons.FOLDER_OPEN,
                            ft.Colors.BLUE,
                        ),
                        _build_summary_card(
                            "Pending Tasks",
                            "12",
                            ft.Icons.TASK_ALT,
                            ft.Colors.ORANGE,
                        ),
                        _build_summary_card(
                            "Team Members", "8", ft.Icons.PEOPLE, ft.Colors.GREEN
                        ),
                        _build_summary_card(
                            "System Alerts", "0", ft.Icons.WARNING, ft.Colors.RED
                        ),
                    ],
                    wrap=True,
                    spacing=20,
                    run_spacing=20,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )


def _build_summary_card(title: str, value: str, icon_name: str, color: str):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(name=icon_name, color=color, size=30),
                ft.Text(value, size=30, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=14, color=ft.Colors.GREY_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=200,
        height=150,
        bgcolor=ft.Colors.GREY_800,  # Using standard grey for better dark mode look
        border_radius=10,
        padding=20,
        alignment=ft.Alignment(0, 0),
    )
