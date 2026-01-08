import flet as ft
from sysengn.core.auth import User


class DocsScreen(ft.Container):
    """A screen for displaying documentation with a side rail and drawer."""

    def __init__(self, page: ft.Page, user: User):
        super().__init__()
        self.page_ref = page
        self.user = user
        self.expand = True

        # Drawer Content State
        self.drawer_content = ft.Text("Outline Content", size=14)

        # We need a reference to the drawer content container to update it
        self.drawer_container_ref = ft.Ref[ft.Container]()

        # Side Rail
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.NONE,
            min_width=50,
            min_extended_width=150,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.FORMAT_LIST_BULLETED,
                    selected_icon=ft.Icons.FORMAT_LIST_BULLETED,
                    label="Outline",
                    padding=ft.padding.symmetric(vertical=10),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER,
                    selected_icon=ft.Icons.FOLDER_OPEN,
                    label="File System",
                    padding=ft.padding.symmetric(vertical=10),
                ),
            ],
            on_change=self.on_rail_change,
            bgcolor=ft.Colors.GREY_900,
        )

        # Drawer Container
        drawer = ft.Container(
            ref=self.drawer_container_ref,
            content=self.drawer_content,
            width=250,
            bgcolor=ft.Colors.GREY_800,
            padding=10,
            border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_700)),
        )

        # Main Content Area
        main_content = ft.Container(
            padding=20,
            content=ft.Column(
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
            ),
            expand=True,
        )

        # Layout: Rail | Drawer | Main Content
        self.content = ft.Row(
            controls=[
                rail,
                drawer,
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_700),
                main_content,
            ],
            expand=True,
            spacing=0,
        )

    def on_rail_change(self, e):
        selected_index = e.control.selected_index
        new_content = ft.Text("Unknown Selection")
        if selected_index == 0:
            new_content = ft.Text("Outline Content", size=14)
        elif selected_index == 1:
            new_content = ft.Text("File System Content", size=14)

        if self.drawer_container_ref.current:
            self.drawer_container_ref.current.content = new_content
            self.drawer_container_ref.current.update()
