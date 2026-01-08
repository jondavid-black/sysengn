import flet as ft
from sysengn.core.auth import User
from typing import Any


class DocsScreen(ft.Container):
    """A screen for displaying documentation with a side rail and drawer."""

    def __init__(self, page: ft.Page, user: User):
        super().__init__()
        self.page_ref = page
        self.user = user
        self.expand = True

        # Mock Data for Docs Tree
        self.docs_data = [
            {
                "id": "doc1",
                "title": "Project Specification",
                "type": "document",
                "children": [
                    {
                        "id": "sec1",
                        "title": "1. Introduction",
                        "type": "section",
                        "children": [],
                    },
                    {
                        "id": "sec2",
                        "title": "2. Scope",
                        "type": "section",
                        "children": [
                            {
                                "id": "subsec1",
                                "title": "2.1 In Scope",
                                "type": "section",
                                "children": [],
                            }
                        ],
                    },
                ],
            },
            {"id": "doc2", "title": "User Manual", "type": "document", "children": []},
        ]

        # Initial Drawer Content (Outline)
        self.drawer_content = self._build_outline_view()

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
            width=300,  # Increased width for tree
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

    def _build_outline_view(self) -> ft.Control:
        """Builds the outline view with 'New' button and Tree."""

        def create_new(e):
            # Placeholder for create logic
            print("Create new document/section clicked")
            pass

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Outline", weight=ft.FontWeight.BOLD, size=16),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            tooltip="New Document/Section",
                            icon_size=20,
                            on_click=create_new,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_700),
                ft.Container(
                    content=ft.Column(
                        controls=self._build_tree_nodes(self.docs_data),
                        scroll=ft.ScrollMode.AUTO,
                        spacing=5,
                    ),
                    expand=True,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def _build_tree_nodes(
        self, nodes: list[dict[str, Any]], level: int = 0
    ) -> list[ft.Control]:
        """Recursively builds tree nodes."""
        controls = []
        for node in nodes:
            # Node Row
            node_row = ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.ARTICLE
                        if node["type"] == "document"
                        else ft.Icons.SUBDIRECTORY_ARROW_RIGHT,
                        size=16,
                        color=ft.Colors.BLUE_200
                        if node["type"] == "document"
                        else ft.Colors.GREY_400,
                    ),
                    ft.Text(
                        node["title"],
                        size=14,
                        weight=ft.FontWeight.W_500
                        if node["type"] == "document"
                        else ft.FontWeight.NORMAL,
                        expand=True,
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Delete",
                        on_click=lambda e, n=node: self._delete_node(n),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            )

            # Indent based on level
            controls.append(
                ft.Container(
                    content=node_row,
                    padding=ft.padding.only(left=level * 20),
                    data=node["id"],
                )
            )

            # Recursively add children
            if node.get("children"):
                controls.extend(self._build_tree_nodes(node["children"], level + 1))

        return controls

    def _delete_node(self, node: dict[str, Any]):
        """Placeholder for delete logic."""
        print(f"Delete requested for {node['title']}")
        # In real app: Remove from data, rebuild tree, update UI
        pass

    def on_rail_change(self, e):
        selected_index = e.control.selected_index
        new_content = ft.Text("Unknown Selection")

        if selected_index == 0:
            new_content = self._build_outline_view()
        elif selected_index == 1:
            new_content = ft.Text("File System Content", size=14)

        if self.drawer_container_ref.current:
            self.drawer_container_ref.current.content = new_content
            self.drawer_container_ref.current.update()
