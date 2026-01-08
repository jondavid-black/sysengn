import flet as ft
from typing import Any
from sysengn.core.auth import User
from sysengn.core.project_manager import ProjectManager


class SEScreen(ft.Container):
    """The Systems Engineering Screen component with Side Rail and Drawer."""

    def __init__(self, page: ft.Page, user: User):
        super().__init__()
        self.expand = True
        self.page_ref = page
        self.user = user

        current_project_id = page.session.get("current_project_id")

        if not current_project_id or current_project_id == "Select Project":
            self.content = ft.Column(
                [
                    ft.Icon(ft.Icons.FOLDER_OFF, size=64, color=ft.Colors.GREY_400),
                    ft.Text(
                        "No Project Selected",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Text(
                        "Please select a project from the top banner to view engineering data.",
                        size=14,
                        color=ft.Colors.GREY_500,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            self.alignment = ft.Alignment(0, 0)
            return

        # Fetch project details
        pm = ProjectManager()
        project = pm.get_project(current_project_id)
        self.project_name = project.name if project else "Unknown Project"

        # Mock Data for Trees
        self.containment_data = [
            {
                "id": "sys1",
                "title": "Autonomous Vehicle",
                "type": "system",
                "children": [
                    {
                        "id": "sub1",
                        "title": "Powertrain",
                        "type": "subsystem",
                        "children": [
                            {
                                "id": "comp1",
                                "title": "Battery Pack",
                                "type": "component",
                            },
                            {
                                "id": "comp2",
                                "title": "Electric Motor",
                                "type": "component",
                            },
                        ],
                    },
                    {
                        "id": "sub2",
                        "title": "Perception",
                        "type": "subsystem",
                        "children": [
                            {
                                "id": "comp3",
                                "title": "Lidar Array",
                                "type": "component",
                            },
                            {
                                "id": "comp4",
                                "title": "Camera Module",
                                "type": "component",
                            },
                        ],
                    },
                ],
            }
        ]

        self.spec_data = [
            {
                "id": "spec1",
                "title": "System Requirements",
                "type": "spec",
                "children": [
                    {"id": "req1", "title": "SR-001: Max Speed", "type": "req"},
                    {"id": "req2", "title": "SR-002: Range", "type": "req"},
                ],
            },
            {
                "id": "spec2",
                "title": "Safety Requirements",
                "type": "spec",
                "children": [
                    {
                        "id": "req3",
                        "title": "SAF-001: Emergency Braking",
                        "type": "req",
                    },
                ],
            },
        ]

        # Initial Drawer Content
        self.drawer_container_ref = ft.Ref[ft.Container]()
        self.drawer_content = ft.Text("File System Content", size=14)

        # Side Rail
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.NONE,
            min_width=50,
            min_extended_width=150,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER,
                    selected_icon=ft.Icons.FOLDER_OPEN,
                    label="File System",
                    padding=ft.padding.symmetric(vertical=10),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ACCOUNT_TREE_OUTLINED,
                    selected_icon=ft.Icons.ACCOUNT_TREE,
                    label="Containment Tree",
                    padding=ft.padding.symmetric(vertical=10),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIST_ALT_OUTLINED,
                    selected_icon=ft.Icons.LIST_ALT,
                    label="Specification Tree",
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

        # Main Content Area (Tabs)
        main_content = ft.Container(
            padding=20,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                f"MBSE: {self.project_name}",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Chip(
                                label=ft.Text("Requirements"),
                                leading=ft.Icon(ft.Icons.LIST_ALT),
                                selected=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=20,
                    ),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Tabs(
                            selected_index=0,
                            animation_duration=300,
                            tabs=[
                                ft.Tab(
                                    text="Requirements",
                                    icon=ft.Icons.RULE,
                                    content=ft.Container(
                                        content=ft.Text(
                                            "Requirements List Placeholder"
                                        ),
                                        padding=20,
                                    ),
                                ),
                                ft.Tab(
                                    text="Functions",
                                    icon=ft.Icons.FUNCTIONS,
                                    content=ft.Container(
                                        content=ft.Text(
                                            "Functional Architecture Placeholder"
                                        ),
                                        padding=20,
                                    ),
                                ),
                                ft.Tab(
                                    text="Components",
                                    icon=ft.Icons.MEMORY,
                                    content=ft.Container(
                                        content=ft.Text(
                                            "Physical Architecture Placeholder"
                                        ),
                                        padding=20,
                                    ),
                                ),
                            ],
                            expand=True,
                        ),
                        expand=True,
                    ),
                ],
                expand=True,
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
            new_content = ft.Text("File System Content", size=14)
        elif selected_index == 1:
            new_content = self._build_tree_view(
                "Containment", self.containment_data, ft.Icons.ADD_BOX
            )
        elif selected_index == 2:
            new_content = self._build_tree_view(
                "Specifications", self.spec_data, ft.Icons.NOTE_ADD
            )

        if self.drawer_container_ref.current:
            self.drawer_container_ref.current.content = new_content
            self.drawer_container_ref.current.update()

    def _build_tree_view(
        self, title: str, data: list[dict[str, Any]], add_icon: str
    ) -> ft.Control:
        """Builds a generic tree view with a header."""
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                        ft.IconButton(
                            icon=add_icon,
                            tooltip=f"New {title}",
                            icon_size=20,
                            on_click=lambda e: print(f"New {title} clicked"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_700),
                ft.Container(
                    content=ft.Column(
                        controls=self._build_tree_nodes(data),
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
            # Determine Icon based on type
            icon = ft.Icons.CIRCLE
            color = ft.Colors.GREY_400

            node_type = node.get("type", "")
            if node_type == "system":
                icon = ft.Icons.TOKEN
                color = ft.Colors.PURPLE_300
            elif node_type == "subsystem":
                icon = ft.Icons.DASHBOARD_CUSTOMIZE
                color = ft.Colors.BLUE_300
            elif node_type == "component":
                icon = ft.Icons.MEMORY
                color = ft.Colors.GREEN_300
            elif node_type == "spec":
                icon = ft.Icons.DESCRIPTION
                color = ft.Colors.ORANGE_300
            elif node_type == "req":
                icon = ft.Icons.RULE
                color = ft.Colors.YELLOW_300

            # Node Row
            node_row = ft.Row(
                controls=[
                    ft.Icon(icon, size=16, color=color),
                    ft.Text(
                        node["title"],
                        size=14,
                        expand=True,
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
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
