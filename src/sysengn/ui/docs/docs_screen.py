import flet as ft
from sysengn.core.auth import User


class DocsScreen(ft.Container):
    """A screen for displaying documentation.

    This is a mock implementation that displays a placeholder for the docs.
    """

    def __init__(self, page: ft.Page, user: User):
        super().__init__()
        self.page_ref = page
        self.user = user
        self.expand = True

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "Documentation",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_200,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.LIBRARY_BOOKS,
                                size=64,
                                color=ft.Colors.GREY_500,
                            ),
                            ft.Text(
                                "Documentation Module",
                                size=20,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "Manage and view project documentation here.",
                                color=ft.Colors.GREY_400,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    padding=50,
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=20,
        )
