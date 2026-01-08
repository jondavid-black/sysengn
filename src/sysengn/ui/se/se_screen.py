import flet as ft
from sysengn.core.auth import User
from sysengn.core.project_manager import ProjectManager


def SEScreen(page: ft.Page, user: User) -> ft.Control:
    """The Systems Engineering Screen component."""

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

    # Placeholder content for SE tools
    return ft.Container(
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
