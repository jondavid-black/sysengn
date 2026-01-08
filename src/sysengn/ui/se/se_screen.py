import flet as ft
from sysengn.core.auth import User
from sysengn.core.project_manager import ProjectManager


def SEScreen(page: ft.Page, user: User) -> ft.Control:
    """The Systems Engineering Screen component with Side Rail and Drawer."""

    current_project_id = page.session.get("current_project_id")

    if not current_project_id or current_project_id == "Select Project":
        return ft.Container(
            content=ft.Column(
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
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )

    # Fetch project details
    pm = ProjectManager()
    project = pm.get_project(current_project_id)
    project_name = project.name if project else "Unknown Project"

    # Drawer Content State
    drawer_content = ft.Text("File System Content", size=14)

    # We need a reference to the drawer content container to update it
    drawer_container_ref = ft.Ref[ft.Container]()

    def on_rail_change(e):
        selected_index = e.control.selected_index
        new_content = ft.Text("Unknown Selection")
        if selected_index == 0:
            new_content = ft.Text("File System Content", size=14)
        elif selected_index == 1:
            new_content = ft.Text("Containment Tree Content", size=14)
        elif selected_index == 2:
            new_content = ft.Text("Specification Tree Content", size=14)

        if drawer_container_ref.current:
            drawer_container_ref.current.content = new_content
            drawer_container_ref.current.update()

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
        on_change=on_rail_change,
        bgcolor=ft.Colors.GREY_900,
    )

    # Drawer Container
    drawer = ft.Container(
        ref=drawer_container_ref,
        content=drawer_content,
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
                            f"MBSE: {project_name}", size=28, weight=ft.FontWeight.BOLD
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
                                    content=ft.Text("Requirements List Placeholder"),
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
    return ft.Row(
        controls=[
            rail,
            drawer,
            ft.VerticalDivider(width=1, color=ft.Colors.GREY_700),
            main_content,
        ],
        expand=True,
        spacing=0,
    )
